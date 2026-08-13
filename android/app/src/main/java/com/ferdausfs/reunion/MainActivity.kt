package com.ferdausfs.reunion

import android.annotation.SuppressLint
import android.app.Activity
import android.graphics.Bitmap
import android.os.Bundle
import android.util.Log
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient

/**
 * "AI Model Family Reunion" — a native WebView wrapper for the single-file HTML page.
 *
 * Loads [PAGE_URL] (bundled in assets, so it works fully offline) and keeps the
 * page inside the WebView. Every lifecycle step logs a marker under the
 * [TAG] tag so the flow is observable with:
 *
 *   adb logcat -s REUNION_APP
 */
class MainActivity : Activity() {

    companion object {
        private const val TAG = "REUNION_APP"
        private const val PAGE_URL = "file:///android_asset/reunion.html"
    }

    private lateinit var webView: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "onCreate: configuring WebView, will load assets/reunion.html")

        webView = WebView(this)
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = true
            allowContentAccess = true
            loadWithOverviewMode = true
            useWideViewPort = true
            builtInZoomControls = false
            displayZoomControls = false
            cacheMode = WebSettings.LOAD_DEFAULT
            mixedContentMode = WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE
        }

        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                super.onPageStarted(view, url, favicon)
                Log.d(TAG, "onPageStarted: url=$url")
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                Log.d(TAG, "onPageFinished: url=$url")
            }

            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                // The page only links to its own in-page anchors, so stay inside the WebView.
                Log.d(TAG, "shouldOverrideUrlLoading: url=${request?.url}")
                return false
            }
        }
        webView.webChromeClient = WebChromeClient()

        setContentView(webView)
        webView.loadUrl(PAGE_URL)
        Log.d(TAG, "onCreate: loadUrl dispatched for $PAGE_URL")
    }

    @Suppress("DEPRECATION")
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            Log.d(TAG, "onBackPressed: navigating back inside WebView")
            webView.goBack()
        } else {
            Log.d(TAG, "onBackPressed: no WebView history — finishing activity")
            super.onBackPressed()
        }
    }

    override fun onDestroy() {
        Log.d(TAG, "onDestroy: destroying WebView")
        webView.destroy()
        super.onDestroy()
    }
}
