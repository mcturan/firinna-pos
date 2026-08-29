const fs = require('fs');

let content = fs.readFileSync('/opt/firinna-pos/web/script.js', 'utf8');

// The translator used double quotes and hard newlines inside `text_about` and maybe others.
// We can replace the specific fields if we know them, or we can use a regex to convert all unescaped newlines inside strings to \n.
// Since it's easier, let's just replace `text_about: "` ... `",` with backticks, or just escape it manually.

// Find all occurrences of text_about
content = content.replace(/text_about:\s*"([^"]*)"/g, (match, p1) => {
    return 'text_about: `' + p1.replace(/`/g, '\\`') + '`';
});

content = content.replace(/social_intro:\s*"([^"]*)"/g, (match, p1) => {
    return 'social_intro: `' + p1.replace(/`/g, '\\`') + '`';
});

content = content.replace(/menu_intro:\s*"([^"]*)"/g, (match, p1) => {
    return 'menu_intro: `' + p1.replace(/`/g, '\\`') + '`';
});

content = content.replace(/desc_p1:\s*"([^"]*)"/g, (match, p1) => {
    return 'desc_p1: `' + p1.replace(/`/g, '\\`') + '`';
});

// Since the error showed line 172, let's check what exactly failed.
fs.writeFileSync('/opt/firinna-pos/web/script.js', content);
