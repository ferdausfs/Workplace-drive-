#!/usr/bin/env node
/**
 * Deriv API connectivity + trading test (demo)
 * - connect (app_id from env or prompt, default 1089)
 * - authorize with API token (hidden input, NEVER printed)
 * - active_symbols → list forex/crypto/synthetic
 * - tick stream for one symbol
 * - proposal (price for a CALL) — no buy yet (use --buy to place $1 demo trade)
 *
 * Usage: node deriv-test.mjs [--buy]
 */
import WebSocket from 'ws';
import readline from 'readline';

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const ask = (q) => new Promise((res) => rl.question(q, res));

const ARGS = process.argv.slice(2);
const DO_BUY = ARGS.includes('--buy');

async function main() {
  const app_id = process.env.DERIV_APP_ID || (await ask('App ID (Enter = 1089): ')) || '1089';
  let token = process.env.DERIV_API_TOKEN;
  if (!token) {
    token = await new Promise((res) => {
      const rl2 = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: true });
      process.stdout.write('API Token (hidden): ');
      // disable echo
      const orig = process.stdout.write.bind(process.stdout);
      process.stdout.write = (s) => orig(s.replace(/[^\n]/g, '\u0008\u0000').replace(/\u0000/g, '') );
      rl2.question('', (ans) => { process.stdout.write = orig; console.log(''); rl2.close(); res(ans.trim()); });
    });
  }
  if (!token || token.length < 10) { console.error('❌ token missing'); process.exit(1); }

  const url = `wss://ws.derivws.com/websockets/v3?app_id=${app_id}`;
  console.log(`\n🔌 connecting ${url} ...`);
  const ws = new WebSocket(url);
  const timeout = setTimeout(() => { console.error('⏰ timeout'); process.exit(1); }, 25000);

  ws.on('open', () => {
    console.log('✅ connected');
    ws.send(JSON.stringify({ authorize: token }));
  });

  ws.on('message', async (d) => {
    const data = JSON.parse(d.toString());
    const mt = data.msg_type;

    if (mt === 'authorize') {
      if (data.error) { console.error('❌ authorize error:', data.error.message); process.exit(1); }
      const acct = data.authorize;
      console.log('✅ authorized as:', acct.currency, '| balance:', acct.balance, '| account:', acct.loginid);
      console.log('   landing_company:', acct.landing_company_name, '| is_virtual:', acct.is_virtual, '(demo=1 ✓)');
      ws.send(JSON.stringify({ active_symbols: 'brief' }));
    }
    else if (mt === 'active_symbols') {
      if (data.error) { console.error('❌ symbols error:', data.error.message); process.exit(1); }
      const syms = data.active_symbols || [];
      console.log(`\n✅ active_symbols: ${syms.length}`);
      const types = {};
      for (const s of syms) types[s.symbol_type] = (types[s.symbol_type]||0)+1;
      console.log('   types:', JSON.stringify(types));
      const forex = syms.filter(s=>s.symbol_type==='forex').slice(0,6).map(s=>`${s.symbol}(${s.display_name})`);
      const cry = syms.filter(s=>s.symbol_type==='cryptocurrency').slice(0,6).map(s=>`${s.symbol}(${s.display_name})`);
      const syn = syms.filter(s=>s.symbol_type==='synthetic_index').slice(0,6).map(s=>`${s.symbol}(${s.display_name})`);
      console.log('   forex:', forex.join(', '));
      console.log('   crypto:', cry.join(', '));
      console.log('   synthetic:', syn.join(', '));
      // pick a symbol to test ticks: prefer EURUSD forex, else first symbol
      const pick = syms.find(s=>s.symbol_type==='forex' && s.symbol.includes('EUR')) || syms[0];
      console.log(`\n📡 tick stream: ${pick.symbol}`);
      ws.send(JSON.stringify({ ticks: pick.symbol, subscribe: 1 }));
    }
    else if (mt === 'tick') {
      if (data.error) { console.error('❌ tick error:', data.error.message); process.exit(1); }
      console.log(`   tick ${data.tick.symbol}: ${data.tick.quote}`);
      // proposal for a 5-min CALL (digital option) — matches our OTC style
      const sym = data.tick.symbol;
      const proposalReq = { proposal: 1, amount: 1, basis: 'stake', contract_type: 'CALL', currency: 'USD', duration: 5, duration_unit: 'm', symbol: sym };
      console.log(`\n💡 proposal: CALL 5min on ${sym} (stake $1)...`);
      ws.send(JSON.stringify(proposalReq));
    }
    else if (mt === 'proposal') {
      if (data.error) { console.error('❌ proposal error:', data.error.message, JSON.stringify(data.error)); process.exit(1); }
      const p = data.proposal;
      console.log('   proposal:', p.longcode);
      console.log('   ask_price:', p.ask_price, '| payout:', p.payout, '| id:', p.id);
      if (DO_BUY) {
        console.log('\n💰 BUYING (demo)...');
        ws.send(JSON.stringify({ buy: p.id, price: p.ask_price }));
      } else {
        console.log('\n✅ proposal OK — (--buy flag na dile trade hoy na. demo trade test: node deriv-test.mjs --buy)');
        process.exit(0);
      }
    }
    else if (mt === 'buy') {
      if (data.error) { console.error('❌ buy error:', data.error.message); process.exit(1); }
      const b = data.buy;
      console.log('✅ BOUGHT! contract_id:', b.contract_id, '| longcode:', b.longcode);
      console.log('   (result track: proposal_open_contract — demo money)');
      process.exit(0);
    }
    else if (data.error) {
      console.error('API error:', JSON.stringify(data.error).slice(0,200));
      process.exit(1);
    }
  });

  ws.on('error', (e) => { console.error('WS error:', e.message); clearTimeout(timeout); process.exit(1); });
}

main().catch(e => { console.error(e); process.exit(1); });
