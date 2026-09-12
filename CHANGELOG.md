## [1.3.5](https://github.com/lukislp/Lagersystem-hacs/compare/v1.3.4...v1.3.5) (2026-09-12)


### Bug Fixes

* **ci:** bump dependabot/fetch-metadata from 2.5.0 to 3.1.0 ([7c74b15](https://github.com/lukislp/Lagersystem-hacs/commit/7c74b15eb2b7ae8d85521e06422e1efd89763327))
* **ci:** bump github/codeql-action/upload-sarif from 3.38.0 to 4.38.0 ([52695d2](https://github.com/lukislp/Lagersystem-hacs/commit/52695d20194bc045fc84a209334272b0acda7e3d))

## [1.3.4](https://github.com/lukislp/Lagersystem-hacs/compare/v1.3.3...v1.3.4) (2026-09-12)


### Bug Fixes

* run on Home Assistant 2026.9 and test against it on Python 3.14 ([#8](https://github.com/lukislp/Lagersystem-hacs/issues/8)) ([b4fb3a7](https://github.com/lukislp/Lagersystem-hacs/commit/b4fb3a77faced98545ee343f953ae0bf89873339))

## [1.3.3](https://github.com/lukislp/Lagersystem-hacs/compare/v1.3.2...v1.3.3) (2026-09-11)


### Bug Fixes

* **ci:** read-only GITHUB_TOKEN in the Dependabot auto-merge workflow ([ddd0361](https://github.com/lukislp/Lagersystem-hacs/commit/ddd03615e71781cc936398908c80c1141a4bd9db))

## [1.3.2](https://github.com/lukislp/Lagersystem-hacs/compare/v1.3.1...v1.3.2) (2026-09-11)


### Bug Fixes

* **ci:** push release commits as a deploy key so the default branch can be ruleset-protected ([c5f2871](https://github.com/lukislp/Lagersystem-hacs/commit/c5f28713178becb2d5cff57a38effadfc2886079))

## [1.3.1](https://github.com/lukislp/Lagersystem-hacs/compare/v1.3.0...v1.3.1) (2026-09-03)


### Bug Fixes

* **ci:** add Dependabot for github-actions, pip ([71b6cd6](https://github.com/lukislp/Lagersystem-hacs/commit/71b6cd6ae4155a40660860c4e932f40e24ee2077))

# [1.3.0](https://github.com/lukislp/Lagersystem-hacs/compare/v1.2.0...v1.3.0) (2026-08-05)


### Features

* add a self-hosted test coverage badge ([746cd6b](https://github.com/lukislp/Lagersystem-hacs/commit/746cd6b86b6bf1e1b705ca959d6e45d4e427613c))

# [1.2.0](https://github.com/lukislp/Lagersystem-hacs/compare/v1.1.1...v1.2.0) (2026-08-05)


### Bug Fixes

* stop skipping the hacs brands check now that a local icon exists ([85b0473](https://github.com/lukislp/Lagersystem-hacs/commit/85b04731758a50b66a27f5d1b929eea58e82647c))


### Features

* add local brand icon via Home Assistant's brand proxy API ([20fbe3c](https://github.com/lukislp/Lagersystem-hacs/commit/20fbe3cbb1ff7de56a2c68908a2377d20501c218))

## [1.1.1](https://github.com/lukislp/Lagersystem-hacs/compare/v1.1.0...v1.1.1) (2026-08-05)


### Bug Fixes

* surface build/release/license/HACS status via README badges ([bab23a0](https://github.com/lukislp/Lagersystem-hacs/commit/bab23a06a001d4f35bc0068889026a5cc2201241))

# [1.1.0](https://github.com/lukislp/Lagersystem-hacs/compare/v1.0.0...v1.1.0) (2026-08-05)


### Bug Fixes

* don't swallow config flow's duplicate-entry abort as a generic error ([11ddc17](https://github.com/lukislp/Lagersystem-hacs/commit/11ddc17b58f2dae7de4875310deb0d1905c6244c))
* remove URL from host field translation string ([cc24a98](https://github.com/lukislp/Lagersystem-hacs/commit/cc24a985fd1733f0db74bfa7c8fdafb13b211477))


### Features

* add CI/CD pipeline and full pytest coverage for the integration ([783216d](https://github.com/lukislp/Lagersystem-hacs/commit/783216d4b763c1cbc98a2c3429e1ce7278ad5db4))
