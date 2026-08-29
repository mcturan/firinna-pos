const fs = require('fs');

const content = fs.readFileSync('/opt/firinna-pos/web/script.js', 'utf8');

// Use regex to extract the i18n object definition
const match = content.match(/const i18n = (\{[\s\S]*?\n\});/);
if (match) {
    fs.writeFileSync('/opt/firinna-pos/web/i18n_dump.txt', match[1]);
    console.log("Dumped i18n");
} else {
    console.log("Could not find i18n");
}
