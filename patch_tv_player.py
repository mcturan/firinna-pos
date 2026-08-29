import re

with open("/opt/firinna-pos/templates/tv_player.html", "r") as f:
    content = f.read()

# I will just edit `playLocalVideo(vIndex)` to always play directly without background queue.
old_func = """        async function playLocalVideo(vIndex) {
            let activeList = (localVideoList && localVideoList.length > 0) ? localVideoList : CORE_FALLBACK_VIDEOS;
            currentLocalVideoIndex = vIndex % activeList.length;
            let rawVideo = activeList[currentLocalVideoIndex];
            if (!rawVideo) rawVideo = "/static/tv_media/videos/bayrak.mp4";
            
            let srcUrl = rawVideo;
            if (!srcUrl.startsWith("/static/")) { srcUrl = "/static/tv_media/videos/" + srcUrl; }
            const filename = srcUrl.split('/').pop();

            // 1. Check memory or persistent disk cache
            let blobUrl = bufferedVideoBlobs[srcUrl];
            if (!blobUrl) {
                blobUrl = await checkAndLoadPersistentVideo(srcUrl);
            }

            if (blobUrl) {
                isPlayingFallback = false;
                tvLog(`[PLAYBACK] Playing ready cached video: ${filename}`);
                playBlobDirectly(blobUrl, srcUrl);
                return;
            }

            // 2. Pure fallback video
            if (srcUrl.endsWith('/bayrak.mp4')) {
                isPlayingFallback = true;
                tvLog(`[PLAYBACK] Playing core fallback: bayrak.mp4`);
                playBlobDirectly(srcUrl, srcUrl);
                return;
            }

            // 3. Custom video is downloading in background:
            // Ensure queued in background sync
            queueVideoForBackgroundDownload(srcUrl);

            // While waiting for download, play fallback bayrak.mp4 so screen is NEVER blank or interrupted
            isPlayingFallback = true;
            tvLog(`[PLAYBACK WAIT] ${filename} is downloading in background -> Playing fallback bayrak.mp4 in meantime`);
            playBlobDirectly("/static/tv_media/videos/bayrak.mp4", "/static/tv_media/videos/bayrak.mp4");
        }"""

new_func = """        async function playLocalVideo(vIndex) {
            let activeList = (localVideoList && localVideoList.length > 0) ? localVideoList : CORE_FALLBACK_VIDEOS;
            currentLocalVideoIndex = vIndex % activeList.length;
            let rawVideo = activeList[currentLocalVideoIndex];
            if (!rawVideo) rawVideo = "/static/tv_media/videos/bayrak.mp4";
            
            let srcUrl = rawVideo;
            if (!srcUrl.startsWith("/static/")) { srcUrl = "/static/tv_media/videos/" + srcUrl; }
            const filename = srcUrl.split('/').pop();

            // Direct streaming - Caching logic removed to prevent 1GB+ OOM crashes on TV stick
            isPlayingFallback = false;
            tvLog(`[PLAYBACK STREAM] Playing video directly from network: ${filename}`);
            playBlobDirectly(srcUrl, srcUrl);
        }"""

content = content.replace(old_func, new_func)

# Also disable the syncAllPlaylistVideosInBackground so it doesn't queue all on boot
old_sync = """        async function syncAllPlaylistVideosInBackground() {
            let activeList = (localVideoList && localVideoList.length > 0) ? localVideoList : CORE_FALLBACK_VIDEOS;
            tvLog(`[SYNC] Checking disk cache for playlist: ${activeList.join(', ')}`);
            for (let v of activeList) {
                let url = v.startsWith("/static/") ? v : "/static/tv_media/videos/" + v;
                queueVideoForBackgroundDownload(url);
            }
        }"""

new_sync = """        async function syncAllPlaylistVideosInBackground() {
            // Disabled background sync to prevent Out Of Memory (OOM) crashes with large videos.
            // Videos will stream normally.
            tvLog(`[SYNC DISABLED] Direct streaming enabled. Caching skipped for memory safety.`);
        }"""
        
content = content.replace(old_sync, new_sync)

with open("/opt/firinna-pos/templates/tv_player.html", "w") as f:
    f.write(content)
