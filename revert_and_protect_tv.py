import re

with open("/opt/firinna-pos/templates/tv_player.html", "r") as f:
    content = f.read()

# 1. Restore playLocalVideo but with stream fallback logic integration
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

restored_func = """        async function playLocalVideo(vIndex) {
            let activeList = (localVideoList && localVideoList.length > 0) ? localVideoList : CORE_FALLBACK_VIDEOS;
            currentLocalVideoIndex = vIndex % activeList.length;
            let rawVideo = activeList[currentLocalVideoIndex];
            if (!rawVideo) rawVideo = "/static/tv_media/videos/bayrak.mp4";
            
            let srcUrl = rawVideo;
            if (!srcUrl.startsWith("/static/")) { srcUrl = "/static/tv_media/videos/" + srcUrl; }
            const filename = srcUrl.split('/').pop();

            // 1. Safety Check: If marked as stream-only (due to large size), stream directly
            if (window.streamOnlyVideos && window.streamOnlyVideos[srcUrl]) {
                isPlayingFallback = false;
                tvLog(`[PLAYBACK STREAM] File too large for RAM cache. Streaming directly: ${filename}`);
                playBlobDirectly(srcUrl, srcUrl);
                return;
            }

            // 2. Check memory or persistent disk cache
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

            // 3. Pure fallback video
            if (srcUrl.endsWith('/bayrak.mp4')) {
                isPlayingFallback = true;
                tvLog(`[PLAYBACK] Playing core fallback: bayrak.mp4`);
                playBlobDirectly(srcUrl, srcUrl);
                return;
            }

            // 4. Custom video is downloading in background:
            queueVideoForBackgroundDownload(srcUrl);

            isPlayingFallback = true;
            tvLog(`[PLAYBACK WAIT] ${filename} is downloading... Playing fallback in meantime`);
            playBlobDirectly("/static/tv_media/videos/bayrak.mp4", "/static/tv_media/videos/bayrak.mp4");
        }"""

content = content.replace(new_func, restored_func)

# 2. Restore syncAllPlaylistVideosInBackground
new_sync = """        async function syncAllPlaylistVideosInBackground() {
            // Disabled background sync to prevent Out Of Memory (OOM) crashes with large videos.
            // Videos will stream normally.
            tvLog(`[SYNC DISABLED] Direct streaming enabled. Caching skipped for memory safety.`);
        }"""

restored_sync = """        async function syncAllPlaylistVideosInBackground() {
            let activeList = (localVideoList && localVideoList.length > 0) ? localVideoList : CORE_FALLBACK_VIDEOS;
            tvLog(`[SYNC] Checking disk cache for playlist: ${activeList.join(', ')}`);
            for (let v of activeList) {
                let url = v.startsWith("/static/") ? v : "/static/tv_media/videos/" + v;
                queueVideoForBackgroundDownload(url);
            }
        }"""
content = content.replace(new_sync, restored_sync)

# 3. Add safety mechanism inside processBackgroundDownloadQueue
old_process = """        async function processBackgroundDownloadQueue() {
            if (isDownloadingVideo || videoDownloadQueue.length === 0) return;
            const targetUrl = videoDownloadQueue.shift();
            
            // Re-verify if already cached
            const cachedBlobUrl = await checkAndLoadPersistentVideo(targetUrl);
            if (cachedBlobUrl) {
                processBackgroundDownloadQueue();
                return;
            }"""

safe_process = """        window.streamOnlyVideos = {};

        async function processBackgroundDownloadQueue() {
            if (isDownloadingVideo || videoDownloadQueue.length === 0) return;
            const targetUrl = videoDownloadQueue.shift();
            const filename = targetUrl.split('/').pop();
            
            // Re-verify if already cached
            const cachedBlobUrl = await checkAndLoadPersistentVideo(targetUrl);
            if (cachedBlobUrl) {
                processBackgroundDownloadQueue();
                return;
            }
            
            // SAFETY MECHANISM: Check file size before downloading to prevent RAM OOM Crash
            try {
                const headRes = await fetch(targetUrl, { method: 'HEAD' });
                const size = headRes.headers.get('content-length');
                if (size) {
                    const sizeMB = (parseInt(size) / (1024 * 1024)).toFixed(1);
                    if (parseInt(size) > 150 * 1024 * 1024) { // 150 MB LIMIT
                        tvLog(`[SAFETY GUARD] ${filename} is ${sizeMB}MB (>150MB). Skipping cache to prevent RAM crash. Marked for direct streaming.`);
                        window.streamOnlyVideos[targetUrl] = true;
                        processBackgroundDownloadQueue();
                        return;
                    }
                }
            } catch(e) {
                tvLog(`[SAFETY GUARD] Could not verify size for ${filename}, proceeding with caution.`);
            }"""

content = content.replace(old_process, safe_process)

with open("/opt/firinna-pos/templates/tv_player.html", "w") as f:
    f.write(content)
