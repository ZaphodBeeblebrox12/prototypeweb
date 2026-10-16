const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const script = fs.readFileSync("site/assets/academy-routing.js", "utf8");

function evaluate(baseUrl, initialHrefs) {
  const setting = { content: baseUrl };
  const links = initialHrefs.map(href => ({
    _href: href,
    getAttribute(name) {
      return name === "href" ? this._href : null;
    },
    get href() {
      return this._href;
    },
    set href(value) {
      this._href = value;
    }
  }));
  const document = {
    querySelector(selector) {
      return selector === 'meta[name="academy-base-url"]' ? setting : null;
    },
    querySelectorAll(selector) {
      return selector === "a[href]" ? links : [];
    }
  };
  vm.runInNewContext(script, { document });
  return links.map(link => link.href);
}

const target = "https://tradethesis-academy-staging.onrender.com";
assert.deepEqual(
  evaluate(target + "/", [
    "/learn/",
    "/accounts/login/?next=/learn/",
    "/accounts/signup/?next=/learn/",
    "/accounts/password/reset/",
    "member-area.html",
    "https://example.com/learn/",
    "/not-an-academy-route/"
  ]),
  [
    target + "/learn/",
    target + "/accounts/login/?next=/learn/",
    target + "/accounts/signup/?next=/learn/",
    target + "/accounts/password/reset/",
    "member-area.html",
    "https://example.com/learn/",
    "/not-an-academy-route/"
  ]
);
assert.deepEqual(evaluate("", ["/learn/", "/accounts/login/"]), [
  "/learn/",
  "/accounts/login/"
]);
console.log("Academy routing smoke test passed: auth/learning URLs use the configured host; unrelated links remain unchanged.");
