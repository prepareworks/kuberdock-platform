
# Why webpack?

* ES2016 (+ [object-rest-spread](https://github.com/sebmarkbage/ecmascript-rest-spread) and [decorators](https://github.com/wycats/javascript-decorators/blob/master/README.md) proposals)
* source maps for LESS and everything else
* replace images and other stuff with dataURI
* `npm run dev` -- serve static files directly from localhost/memory
* smaller `prepared.js` and css


# How to build and serve


## Prepare environment (example for ubuntu).


### Install NodeJS


#### using "n":
Using npm-package called "n" you can easily keep many versions of NodeJS and switch between them anytime you want. Run as root:
```
# apt-get install nodejs npm
# npm cache clean -f
# npm install -g n
# n 6.4.0
# ln -sf /usr/local/n/versions/node/6.4.0/bin/node /usr/bin/node
```

#### Or using your package manager, from their official repos:
see https://nodejs.org/en/download/package-manager/


### Install all requirements:
```
$ cd kubedock/frontend/static/
$ yarn install  # will install all dependencies from package.json
```


### Some additional tuning

* If you use eslint (and you should), install `babel-eslint` plugin:
```
npm install -g babel-eslint
```
* Add plugins/modules/packages to your IDE to support ES6. For Atom it would be
```
apm install language-babel
```


## How to make static build
```
$ PROD_ENV=true npm run build
```

## How to run dev-server (127.0.0.1:3000)
Specify your master IP as environment variable or in local-config.js (see config.js).
```
$ API_HOST=192.168.120.7 npm run dev
```


# FAQ

### WTF is dev-server?
Dev-server runs on your local machine. What it does is:
* (Re)Builds `prepared.js` and `prepared.css` on every change in any imported module (in webpack everything is a module, including css, images, fonts and stuff).
* Serves it directly from memory, without saving on disk.
* Serves other static files directly from localhost.
* Proxies all API-requests and other stuff to KuberDock master.

It allows you to avoid syncing all frontend stuff with master and significantly increases page load speed.


### What about `local-config.js`?

There you can specify you own local settings. Here is an example:
```
/* eslint-env node */
module.exports = {
    // assume dev-environment by default: don't minify, keep source-maps, and so on
    PROD: false,
    // IP or hostname of your master machine
    API_HOST: '1.2.3.4',
};
```
See `config.js` for more options/details.


### How to add another dependency?

Find in on [npm](https://www.npmjs.com/).

If you *did* find it, install: `npm install --save-dev some-new-lib`. That's it, you're awesome!

If you couldn't find it on npm:
* first, try to find an alternative. 99.9% of fresh and/or popular libs can be found on npm. If you cannot find it there, it's a sign that this library might be a poor choice.
* if you're still positive on using this library, just put it in `/js/libs/` and add an alias in `webpack.config.js`


# Additional resources
* [webpack documentation](https://webpack.github.io/docs/configuration.html)
