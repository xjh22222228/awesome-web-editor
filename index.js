/**
 * Update star
 * @since 1.1.0
 * @author xiejiahe
 * @example node index.js README_zh-CN.md
 */

const request = require('axios');
const readline = require('readline');
const fs = require('fs');
const { URL } = require('url');
const ora = require('ora');

const FILE_NAME = process.argv.slice(2).pop() || 'README.md'

const spinner = ora({
  text: 'Processing...'
});
spinner.start();

function isUrl(url) {
  try {
    new URL(url);
  } catch {
    return false;
  }
  return true;
}

function getStar(githubUrl) {
  spinner.start(`Waiting for ${githubUrl} results...`);
  const parseUrl = new URL(githubUrl);
  const apiUrl = `https://api.github.com/repos${parseUrl.pathname}`;
  
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      request
      .get(apiUrl)
      .then(res => {
        const star = res.data.stargazers_count;
        if (star) {
          spinner.succeed(`${githubUrl} ★ ${star}`);
          resolve(star);
        }
      })
      .catch(err => {
        spinner.fail(`${err.response.status} failed: ${apiUrl}`);
        reject(err);
      });
    }, 1000 * 60 * 2);
  });
}

;(async () => {
  let contents = [];
  const filePath = FILE_NAME;
  const regex1 = /(★\s{1}\d+)/;
  const regex2 = /\[.{1,}\]\(([^)]{1,})\)/;

  const rl = readline.createInterface({
    input: fs.createReadStream(filePath),
    crlfDelay: Infinity
  });

  rl.on('line', line => {
    contents.push(line);
  });
  
  rl.on('close', async () => {
    for (let i = 0; i < contents.length; i++) {
      const value = contents[i];
      if (regex1.test(value)) {
        const isMatch = value.match(regex2);
        if (isMatch !== null) {
          const url = RegExp.$1;
          if (isUrl(url) && url.startsWith('https://github.com')) {
            try {
              const star = await getStar(url);
              contents[i] = contents[i].replace(regex1, `★ ${star}`);
            } catch {}
          }
        }
      }
    }

    fs.writeFileSync(filePath, contents.join('\r'));
    spinner.stop();
    console.log('Completed!');
  });
})();
