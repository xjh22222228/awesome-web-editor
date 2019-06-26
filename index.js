/**
 * Star update once a month.
 * @since 1.0.0
 * @author xiejiahe
 */

const request = require('axios');
const readline = require('readline');
const fs = require('fs');
const { URL } = require('url');
const ora = require('ora');

const spinner = ora({
  text: 'Processing...',
});
spinner.start();


function isUrl(url) {
  try {
    new URL(url);
  } catch (error) {
    return false;
  }
  return true;
}

/**
 * Request every 10 seconds，
 * @param {String} githubUrl
 * @returns {Promise}
 */
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
        spinner.fail(`failed: ${githubUrl}`);
        reject(err);
      });
    }, 10000);
  });
}

;(async () => {
  let contents = [];
  const filePath = './README.md';

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
          if (isUrl(url)) {
            try {
              const star = await getStar(url);
              contents[i] = contents[i].replace(regex1, `★ ${star}`);
            } catch (err) {

            }
          } else {
            console.log(`no url: ${url}`);
          }
        }
      }
    }

    fs.writeFileSync(filePath, contents.join('\r'));
    spinner.stop();
    console.log('Completed!');
  });
  
})();


