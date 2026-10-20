# Decisions — shanhaijing-gallery

Updated: 2026-10-20

- **2026-10-12** — Gallery is the catalog home; holo-card remains a separate effect playground.
- **2026-10-12** — Artists deliver 4:3 mother art; site crops to 3:4 for presentation.
- **2026-10-12** — Slugs are pinyin (`yinglong`); overrides live in build script / slug-map.
- **2026-10-12** — Copy must be classics-verifiable; art-direction traits (e.g. white-gold wings) stay out of scripture fields.
- **2026-10-12** — Agnir Core/profile `1.0` / `repository-filesystem/1.0` from iorLab/agnir `v1.0.2` (`b5626394ec40a5cb7a28c01892acde07cc0adc8e`).
- **2026-10-12** — 夔 withdrawn to `pending` (art kept on disk) until redraw; do not show as ready while user rejects current art.
- **2026-10-12** — 夔外形身份锁定：Principal 认可 Kai Mu 双体样张 `user-approved-kaimu-lock.png`（证据 sha256 `0a58f2c96b71a7c63bcd4cd998214ff39510777fc0ab9a601cf1adf0ecd1845a`）。后续重画必须以该图为身份母版；侧腰通长扁平可收合板鳍（非鼓起肉脊）、无前胸/腹鳍乱加；在匹配锁定前保持 `pending`，不得把旧 withdrawn 图重新标 ready。
- **2026-10-12** — 出图交付门禁：美术专家必须先对照夔锁定母版（`user-approved-kaimu-lock.png`）自检身份/解剖/板鳍；未通过不得发给 Principal。
- **2026-10-19** — 筛选状态以 URL 查询参数为准（`volume` / `priority` / `ready=1` / `q`），详情仍用 hash；筛选变更用 `replaceState`，不回写历史，便于分享与收藏。
- **2026-10-19** — 名称中的非 BMP 生僻字用自托管 HanaMinB 子集字体兜底（`unicode-range` 限定当前 7 个字，OFL/Hanazono 双许可）；新增生僻字须重新子集化并更新范围，`check_site.py` 会拦未覆盖字符。
- **2026-10-20** — 本地出图路线封存（文件保留，不再投入）：mflux 0.23 只接受 mflux-community 权重（HF 版 20.5GB，含 15.1GB BF16 文本编码器，24GB 机器不可用）；mlx-community 的 4-bit 版（10.5GB，本机 `~/Models/qwen-image-2.1-mlx`）transformer 参数名与 VAE 形状均与 mflux 不匹配，实测加载即失败，其运行时属 diffusers/MLX 系。夔重画仍需外部图像 API 或美术，不得因本地模型存在而假定可自动出图。
