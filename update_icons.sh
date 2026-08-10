#!/bin/bash
LOGO="/opt/firinna-pos/static/uploads/logo.png"
RES="/opt/firinna-pos/mobile_app/android/app/src/main/res"

if [ ! -f "$LOGO" ]; then
    echo "Logo bulunamadi!"
    exit 1
fi

# Resize function
resize_icon() {
    local size=$1
    local out_dir=$2
    local filename=$3
    
    mkdir -p "${RES}/${out_dir}"
    # Use -background none to preserve transparency, -gravity center -extent to pad the logo nicely
    convert "$LOGO" -resize "${size}x${size}" -background none -gravity center -extent "${size}x${size}" "${RES}/${out_dir}/${filename}"
}

# Standard & Round Icons
resize_icon 48 "mipmap-mdpi" "ic_launcher.png"
resize_icon 48 "mipmap-mdpi" "ic_launcher_round.png"
resize_icon 72 "mipmap-hdpi" "ic_launcher.png"
resize_icon 72 "mipmap-hdpi" "ic_launcher_round.png"
resize_icon 96 "mipmap-xhdpi" "ic_launcher.png"
resize_icon 96 "mipmap-xhdpi" "ic_launcher_round.png"
resize_icon 144 "mipmap-xxhdpi" "ic_launcher.png"
resize_icon 144 "mipmap-xxhdpi" "ic_launcher_round.png"
resize_icon 192 "mipmap-xxxhdpi" "ic_launcher.png"
resize_icon 192 "mipmap-xxxhdpi" "ic_launcher_round.png"

# Foreground Icons
resize_icon 108 "mipmap-mdpi" "ic_launcher_foreground.png"
resize_icon 162 "mipmap-hdpi" "ic_launcher_foreground.png"
resize_icon 216 "mipmap-xhdpi" "ic_launcher_foreground.png"
resize_icon 324 "mipmap-xxhdpi" "ic_launcher_foreground.png"
resize_icon 432 "mipmap-xxxhdpi" "ic_launcher_foreground.png"

echo "Ikonlar basariyla guncellendi."
