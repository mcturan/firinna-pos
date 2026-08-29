package com.firinna.posmobile;

import android.app.DownloadManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import android.widget.Toast;
import androidx.core.content.FileProvider;
import com.getcapacitor.BridgeActivity;
import java.io.File;

public class MainActivity extends BridgeActivity {
    
    private long downloadId;
    private BroadcastReceiver receiver;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        WebView webView = bridge.getWebView();
        webView.addJavascriptInterface(new NativeInterface(this), "AndroidNative");
    }

    public class NativeInterface {
        private Context context;

        public NativeInterface(Context context) {
            this.context = context;
        }

        @JavascriptInterface
        public void downloadAndInstall(String url) {
            runOnUiThread(() -> {
                Toast.makeText(context, "Güncelleme indiriliyor...", Toast.LENGTH_LONG).show();

                File destFile = new File(context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), "update.apk");
                if (destFile.exists()) {
                    destFile.delete();
                }

                DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
                request.setTitle("Fırınna Garson Güncelleme");
                request.setDescription("Yeni sürüm indiriliyor...");
                request.setDestinationUri(Uri.fromFile(destFile));
                request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);

                DownloadManager manager = (DownloadManager) context.getSystemService(Context.DOWNLOAD_SERVICE);
                downloadId = manager.enqueue(request);

                receiver = new BroadcastReceiver() {
                    @Override
                    public void onReceive(Context ctx, Intent intent) {
                        long id = intent.getLongExtra(DownloadManager.EXTRA_DOWNLOAD_ID, -1);
                        if (id == downloadId) {
                            try {
                                context.unregisterReceiver(this);
                            } catch (Exception e) {}
                            
                            Uri apkUri;
                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                                apkUri = FileProvider.getUriForFile(context, context.getPackageName() + ".fileprovider", destFile);
                            } else {
                                apkUri = Uri.fromFile(destFile);
                            }

                            Intent installIntent = new Intent(Intent.ACTION_VIEW);
                            installIntent.setDataAndType(apkUri, "application/vnd.android.package-archive");
                            installIntent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                            installIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                            context.startActivity(installIntent);
                        }
                    }
                };

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    context.registerReceiver(receiver, new IntentFilter(DownloadManager.ACTION_DOWNLOAD_COMPLETE), Context.RECEIVER_EXPORTED);
                } else {
                    context.registerReceiver(receiver, new IntentFilter(DownloadManager.ACTION_DOWNLOAD_COMPLETE));
                }
            });
        }
    }
}
