# 生僻字子集字体

`hanamin-b-rare.woff2` 只包含图鉴名称里用到的 7 个非 BMP 汉字，供 `styles.css` 的
`@font-face` 通过 `unicode-range` 兜底：

| 字符 | 码位 | 出现名称 |
| --- | --- | --- |
| 𤞞 | U+2479E | 独𤞞 |
| 𤞤 | U+247A4 | 山𤞤 |
| 𥕿 | U+2557F | 䂿𥕿 |
| 𩿧 | U+29FE7 | 䳋䳅（𪁺𩿧） |
| 𪁺 | U+2A07A | 䳋䳅（𪁺𩿧） |
| 𪃑 | U+2A0D1 | 𪄀𪃑 |
| 𪄀 | U+2A100 | 𪄀𪃑 |

## 来源与许可

- 源字体：HanaMinB（花園明朝 B），取自
  <https://github.com/googlefonts/chinese/tree/gh-pages/fonts/HanaMin>
- 许可：Hanazono Font License / SIL Open Font License 1.1，见同目录
  `LICENSE-HanaMinB.txt`。本子集不使用 OFL 保留字体名（Reserved Font Name），
  CSS 族名使用 `Shanhaijing Rare`。

## 重新生成

新增非 BMP 名称字符时，重新下载 `HanaMinB.ttf` 后子集化：

```bash
pip install fonttools brotli
pyftsubset HanaMinB.ttf --text='𤞞𤞤𥕿𩿧𪁺𪃑𪄀' --flavor=woff2 \
  --no-hinting --desubroutinize --output-file=assets/fonts/hanamin-b-rare.woff2
```

同时更新 `styles.css` 的 `unicode-range` 与上表；`scripts/check_site.py` 会校验
目录里所有非 BMP 字符都落在声明的 `unicode-range` 内。
