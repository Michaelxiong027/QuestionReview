# QuestionReview
A skill to review the English homework/exam questions for some education platform

# 棰樼洰鎵规敼鍏ㄩ噺娴佺▼

鏈」鐩敤浜庝竴娆℃€у鐞?`questions.xlsx` 閲岀殑骞冲彴棰樼洰 URL锛氭浛鎹㈡巿鏉冨拰浠诲姟琛ㄣ€佷笅杞藉钩鍙伴闈笌绛旀鎴浘銆佺敱 Codex 閫愰〉瑙嗚鏍告煡鍏ㄩ儴棰樼洰銆佸啓鍥?Excel锛屽苟鎶婄‘璁ゆ棤璇殑骞冲彴绛旀閿欒鎻愪氦鍥炲钩鍙般€?

鏈祦绋嬩笉渚濊禆 OCR 鍒ゆ柇銆傝剼鏈枃浠跺悕閲屽嵆浣夸繚鐣?`ocr` 瀛楁牱锛屼篃鍙妸瀹冨綋浣滃巻鍙插懡鍚嶏紱棰樼洰鏍￠獙缁撹蹇呴』鐢?Codex 鍩轰簬椤甸潰鎴浘銆佺瓟妗堟埅鍥俱€佸钩鍙拌繑鍥炴暟鎹拰蹇呰鐨勫惉鍔涢煶棰戝畬鎴愩€?

## 蹇呰鏂囦欢

- `questions.xlsx`锛氬浐瀹氫换鍔¤〃锛屼篃鏄渶缁堝啓鍥炵粨鏋滅殑 Excel銆?
- `authorization.txt`锛氬钩鍙版帴鍙?Authorization銆傜敤鎴锋彁渚涙柊鏂囦欢鍚庤鐩栨湰鐩綍鍚屽悕鏂囦欢銆?
- `task_runner_question_ocr_multithread.py`锛氳鍙?Excel锛岃皟鐢ㄥ钩鍙版帴鍙ｏ紝涓嬭浇鏁撮〉鎴浘銆佸崟棰樼瓟妗堟埅鍥惧拰骞冲彴杩斿洖鎶ユ枃銆?
- `codex_visual_review_writer.py`锛氭妸 `_codex_review/results.json` 鍐欏洖 `questions.xlsx`銆?
- `platform_answer_modifier.py`锛氭妸宸茬‘璁ょ殑骞冲彴绛旀閿欒鎻愪氦鍥炲钩鍙般€?
- `qr_audio_extractor.py`锛氳瘑鍒惉鍔涗簩缁寸爜骞跺敖閲忔彁鍙栭煶棰戯紱璇嗗埆澶辫触鏃朵粎鏍囪鏃犳硶璇嗗埆锛屼笉鐚滅瓟妗堛€?
- `_codex_review/results.json`锛欳odex 鏍告煡缁撹鐨勫敮涓€涓棿鐘舵€佹枃浠躲€?
- `_codex_review/platform_modifications.json`锛氬钩鍙版彁浜ゆ棩蹇椼€?
- `screenshots/<run_id>/manifest.json`锛氫笅杞芥竻鍗曪紝鍖呭惈 row銆乸osition銆乸age_id銆乥ook_id銆乹uestions銆乸latform_answers銆乤nswer_image 绛夈€?

## 涓€娆℃€ф墽琛屾祦绋?

### 闈炲惉鍔涒€滅暐鐣ョ暐鈥濆崰浣嶇瓟妗堣鍒?

- 鍙 `manifest.json` 鐨?`questions[].platform_answers` 涓嚭鐜?`鐣ョ暐鐣锛屼笖璇?URL 涓嶆槸鍚姏棰橈紝蹇呴』浼樺厛閫氳繃 Codex 瑙嗚鏍告煡琛ュ嚭姝ｇ‘绛旀骞舵彁浜ゅ钩鍙颁慨鏀广€?
- 鍒ゆ柇渚濇嵁鍙娇鐢?`source_page.jpg`銆乣answer/*.png`銆乣manifest.json`銆乣platform_response.json` 鍜岄闈笂涓嬫枃锛涗笉浣跨敤 OCR 缁撴灉浣滀负鏈€缁堝垽鏂€?
- 鑳藉敮涓€纭畾绛旀鏃讹紝鏍囪涓?`鏈夐敊璇紝宸蹭慨鏀筦锛屽啓鍏?`answer_updates`锛屽苟閫氳繃 `platform_answer_modifier.py` 鎻愪氦骞冲彴銆傞€夋嫨棰樻彁浜ら€夐」瀛楁瘝锛涘～绌恒€佺炕璇戙€佽繛璇嶆垚鍙ユ彁浜ゆ枃鏈瓟妗堬紱鏁寸粍鍖归厤棰樺彲鎻愪氦鎸夐鍙烽『搴忔帓鍒楃殑绛旀涓层€?
- 姣忔潯 `鏈夐敊璇紝宸蹭慨鏀筦 浠嶇劧鍙繚鐣?1 寮犲钩鍙板師閿欒绛旀鎴浘锛屾埅鍥惧繀椤绘潵鑷搴?URL 鐨?`answer/*.png`銆?
- 濡傛灉闈炲惉鍔?`鐣ョ暐鐣 灞炰簬寮€鏀捐〃杈俱€佷釜浜轰綔绛斻€佷綔鏂囥€佸彛璇嚜鐢卞洖绛旓紝鎴栧繀椤讳緷璧栫己澶卞墠鏂囥€佸浘鐗囥€侀€夐」瀵艰嚧鏃犳硶鍞竴纭畾鏍囧噯绛旀锛屼笉鍏佽缂栭€犵瓟妗堬紱淇濈暀 `瀛樺湪闂锛岄渶浜哄伐纭`锛屽苟鍦?`analysis` 涓槑纭啓鍑哄師鍥犮€?
- 鍚姏棰樹粛鎸夊惉鍔涜鍒欏鐞嗭細鍏堝皾璇曚簩缁寸爜鎴栭煶棰戣瘑鍒紝璇嗗埆澶辫触鏍囪 `鍖呭惈鍚姏锛屼簩缁寸爜鎴栭煶棰戞棤娉曡瘑鍒玚锛屼笉寰椾粎鍑潤鎬侀闈㈢寽绛旀銆?
- 鐤戜技鍚姏棰樹笉鑳藉彧鐪嬩簩缁寸爜鎴栭煶棰戙€傚繀椤诲厛妫€鏌?`platform_response.json` 涓?`labelContainer.answerIndependent.answerText` 鏄惁鍖呭惈鐙珛绛旀鍥剧墖锛堥€氬父鏄?`<img src="...crop...">`锛夈€傚鏋滆鍥剧墖閲屾湁鍚姏鍘熸枃銆佸綍闊虫枃瀛楁垨鍙洿鎺ュ垽鏂瓟妗堢殑鏂囧瓧鍐呭锛屽簲涓嬭浇涓?`independent_answer/` 鎴浘锛岀粨鍚堥闈㈠拰閫夐」鐢?Codex 瑙嗚鏍告煡琛ュ叏绛旀锛屽苟鎸夋櫘閫氬钩鍙扮瓟妗堥敊璇彁浜や慨鏀广€傚彧鏈夌嫭绔嬬瓟妗堝浘銆佷簩缁寸爜鍜岄煶棰戦兘鏃犳硶鎻愪緵鍙垽瀹氬唴瀹规椂锛屾墠鏍囪 `鍖呭惈鍚姏锛屼簩缁寸爜鎴栭煶棰戞棤娉曡瘑鍒玚銆?

### 1. 鏇挎崲杈撳叆

鐢ㄦ埛鍙戞潵鏂扮殑 `authorization.txt` 鍜?Excel 鏃讹細

1. 鐢ㄦ柊鎺堟潈瑕嗙洊鏈洰褰?`authorization.txt`銆?
2. 鐢ㄦ柊 Excel 瑕嗙洊鏈洰褰?`questions.xlsx`銆?
3. 纭涓や釜鏂囦欢瀛樺湪涓旈潪绌恒€?

### 2. 涓嬭浇鍏ㄩ噺椤甸潰鍜岀瓟妗堟埅鍥?

```powershell
.\.venv\Scripts\python.exe .\task_runner_question_ocr_multithread.py --excel .\questions.xlsx --workers 4
```

瀹屾垚鍚庣‘璁わ細

- `screenshots/<run_id>/manifest.json` 宸茬敓鎴愩€?
- 涓嬭浇鎴愬姛鏁扮瓑浜?Excel 涓?URL 鎬绘暟銆?
- 澶辫触鏁颁负 0锛涘鏋滀笅杞藉け璐ワ紝鍏堣В鍐充笅杞介棶棰樺悗閲嶆柊璺戯紝涓嶈繘鍏ユ牳鏌ャ€?

### 3. Codex 涓€娆℃€ф牳鏌ュ叏閮ㄩ鐩?

Codex 鐩存帴鍩轰簬浠ヤ笅鏉愭枡瀹屾垚鍏ㄩ儴棰樼洰鏍告煡锛?

- `source_page.jpg`锛氬師濮嬫暣椤甸闈€?
- `answer/*.png`锛氬钩鍙扮瓟妗堟埅鍥撅紝榛勮壊妗嗗唴涓哄钩鍙板綋鍓嶇瓟妗堛€?
- `manifest.json` 涓搴旈鐩殑 `platform_answers`銆?
- `platform_response.json` 涓湡瀹?`labelContainer.sequence`銆?
- 鍚姏棰樼浉鍏充簩缁寸爜鍜屽彲鎻愬彇闊抽銆?

涓嶅啀鎶?OCR銆侀澶勭悊鎴栧垎鎵硅ˉ鍏呬綔涓哄垽鏂緷鎹€傜湅涓嶆竻鏃舵墦寮€鍘熷浘鏀惧ぇ锛涗粛鏃犳硶纭鏃舵寜瑙勫垯鏍囪涓虹粓鎬侊紝涓嶇寽绛旀銆?

鏍告煡缁撹鍐欏叆 `_codex_review/results.json`銆傛瘡涓?URL 蹇呴』鍦ㄥ悓涓€杞换鍔￠噷缁欏嚭鏈€缁堢姸鎬侊紝涓嶄繚鐣?`寰呰瑙夊鏍竊銆?

### 4. 鍚姏浜岀淮鐮佸鐞?

閬囧埌鍚姏棰樻椂锛屽厛灏介噺閫氳繃浜岀淮鐮佽瘑鍒煶棰戯細

```powershell
.\.venv\Scripts\python.exe .\qr_audio_extractor.py
```

澶勭悊瑙勫垯锛?

- 鑳借瘑鍒簩缁寸爜骞跺彇寰楅煶棰戞椂锛岀粨鍚堥煶棰戝唴瀹瑰畬鎴愮瓟妗堟牳鏌ャ€?
- 浜岀淮鐮佹棤娉曡瘑鍒€侀煶棰戞棤娉曚笅杞姐€侀煶棰戞棤娉曟挱鏀炬垨鍐呭鏃犳硶纭鏃讹紝鏍囪锛?

```text
鍖呭惈鍚姏锛屼簩缁寸爜鎴栭煶棰戞棤娉曡瘑鍒?
```

- 涓嶅厑璁镐粎鍑潤鎬侀闈㈢寽鍚姏绛旀銆?

### 5. 鍐欏叆 results.json

姝ｇ‘棰橈細

```json
{
  "status": "鍏ㄩ儴姝ｇ‘",
  "analysis": "缁?Codex 閫愰〉瑙嗚鏍告煡锛岄闈笌骞冲彴绛旀涓€鑷达紝鏈彂鐜伴渶淇敼鐨勫钩鍙扮瓟妗堛€?,
  "correct_answer": "",
  "answer_updates": [],
  "error_images": []
}
```

骞冲彴绛旀閿欒涓旇兘纭畾姝ｇ‘绛旀锛?

```json
{
  "status": "鏈夐敊璇紝宸蹭慨鏀?,
  "analysis": "璇存槑骞冲彴鍘熺瓟妗堜负浠€涔堥敊锛屼互鍙婃纭瓟妗堜緷鎹€?,
  "correct_answer": "棰樺彿: 姝ｇ‘绛旀",
  "answer_updates": [
    {
      "sequence": "骞冲彴鐪熷疄sequence",
      "answer_index": 1,
      "old_answer": "骞冲彴褰撳墠閿欒绛旀",
      "new_answer": "姝ｇ‘绛旀",
      "new_answer_rich_text": "<p>姝ｇ‘绛旀</p>"
    }
  ],
  "error_images": [
    "骞冲彴鍘熼敊璇瓟妗堟埅鍥捐矾寰?
  ]
}
```

瑕佹眰锛?

- 姣忔潯 `鏈夐敊璇紝宸蹭慨鏀筦 鍙繚鐣?1 寮犲钩鍙板師閿欒绛旀鎴浘銆?
- `error_images` 蹇呴』鎸囧悜 `answer/*.png` 涓兘鐪嬪埌骞冲彴鍘熼敊璇瓟妗堢殑鎴浘銆?
- 鎻愪氦骞冲彴鏃?`sequence` 蹇呴』浣跨敤 `platform_response.json` 閲岀殑鐪熷疄 `labelContainer.sequence`銆?
- 鎴浘鏂囦欢鍚嶅彲鑳芥妸 `44: 20` 瀹夊叏鍖栨垚 `44_20`锛屽彧鑳界敤浜庢壘鍥撅紝涓嶈兘鏇夸唬骞冲彴鐪熷疄 sequence銆?

鏃犳硶纭畾鍞竴姝ｇ‘绛旀锛?

```json
{
  "status": "瀛樺湪闂锛岄渶浜哄伐纭",
  "analysis": "璇存槑鏃犳硶纭鐨勫師鍥犮€?,
  "correct_answer": "",
  "answer_updates": [],
  "error_images": []
}
```

鍚姏鏃犳硶璇嗗埆锛?

```json
{
  "status": "鍖呭惈鍚姏锛屼簩缁寸爜鎴栭煶棰戞棤娉曡瘑鍒?,
  "analysis": "宸插皾璇曡瘑鍒簩缁寸爜/闊抽锛屼絾鏃犳硶鍙栧緱鎴栫‘璁ゅ惉鍔涘唴瀹广€?,
  "correct_answer": "",
  "answer_updates": [],
  "error_images": []
}
```

### 6. 鍐欏洖 Excel

```powershell
.\.venv\Scripts\python.exe .\codex_visual_review_writer.py --excel .\questions.xlsx --results .\_codex_review\results.json
```

鍐欏洖鍚庣‘璁わ細

- 鐘舵€併€佹纭瓟妗堛€侀敊璇垎鏋愬凡鍐欏叆銆?
- `鏈夐敊璇紝宸蹭慨鏀筦 鐨勬瘡涓€琛岄兘鏈変笖鍙湁 1 寮犲钩鍙板師閿欒绛旀鎴浘銆?
- `寰呰瑙夊鏍竊 涓?0銆?

### 7. 鎻愪氦骞冲彴淇敼

鍏?dry-run锛?

```powershell
.\.venv\Scripts\python.exe .\platform_answer_modifier.py --results .\_codex_review\results.json --run-dir .\screenshots\<run_id> --dry-run
```

瑕佹眰 `failed = 0`銆?

姝ｅ紡鎻愪氦锛?

```powershell
.\.venv\Scripts\python.exe .\platform_answer_modifier.py --results .\_codex_review\results.json --run-dir .\screenshots\<run_id>
```

濡傛灉鏈疆瀛樺湪闇€瑕佸洖濉腑鏂囩殑绛旀锛堝鑻辩炕涓€佺煭璇炕璇戯級锛屾彁浜ゅ繀椤讳娇鐢?`platform_answer_modifier.py` 褰撳墠鐨?UTF-8 鎻愪氦閫昏緫锛氳姹備綋浠?`ensure_ascii=False` 鐢熸垚骞朵互 UTF-8 瀛楄妭鍙戦€侊紝`Content-Type` 蹇呴』鍖呭惈 `charset=utf-8`銆傛彁浜ゅ悗瑕侀噸鏂版媺鍙栧搴斿钩鍙伴〉闈紝纭骞冲彴杩斿洖鐨?`answerText` 鍜?`answerRichText` 涓腑鏂囨甯告樉绀猴紝涓嶆槸 `?` 鎴栦贡鐮併€?

濡傛灉闇€瑕佷慨澶嶅凡鎴愬姛鎻愪氦浣嗗钩鍙版樉绀轰负 `?` 鐨勪腑鏂囩瓟妗堬紝鍙己鍒堕噸鎻愬搴旇锛屼笉閲嶅鎻愪氦鍏朵粬琛岋細

```powershell
.\.venv\Scripts\python.exe .\platform_answer_modifier.py --results .\_codex_review\results.json --run-dir .\screenshots\<run_id> --force-row <row>
```

鎻愪氦鍚庢鏌ワ細

```powershell
@'
import json
from pathlib import Path
from collections import Counter
j=json.loads(Path('_codex_review/platform_modifications.json').read_text(encoding='utf-8'))
print(Counter(v.get('status') for v in j.values()))
for row,v in sorted(j.items(), key=lambda kv:int(kv[0])):
    print(row, v.get('status'), len(v.get('updates',[])), v.get('error',''))
'@ | .\.venv\Scripts\python.exe -
```

鎵€鏈夋湁 `answer_updates` 鐨?row 蹇呴』鏄?`success` 鎴栧凡纭鍙烦杩囩殑 `skipped`锛屼笉鑳芥湁 `failed`銆?

## 鍒ら瑙勫垯

- 浠?Codex 瑙嗚鏍告煡涓哄噯锛屼笉鐢?OCR 缁撴灉鍋氭渶缁堝垽鏂€?
- 骞冲彴绛旀鏉ユ簮浠?`manifest.json` 鐨?`questions[].platform_answers` 鍜屽彸渚х瓟妗堟埅鍥句负鍑嗐€?
- `platform_answers` 鎵嶆槸绛旀瀛楁锛屼笉瑕佽鍙栦笉瀛樺湪鐨?`answers` 瀛楁銆?
- 棣栧瓧姣嶈ˉ鍏ㄩ鍙～缂哄け閮ㄥ垎鏄甯哥殑锛屼笉瑕佽鍒や负灏戝瓧姣嶃€?
- 鍦堥€夐鎴栧浘鐗囧尮閰嶉濡傛灉瑙嗚涓婁笌棰橀潰涓€鑷达紝鏍囦负 `鍏ㄩ儴姝ｇ‘`銆?
- 缂哄師鏂囥€侀闈笉瀹屾暣銆佹棤娉曠‘瀹氬敮涓€姝ｇ‘绛旀鏃讹紝鏍囦负 `瀛樺湪闂锛岄渶浜哄伐纭`锛屼笉瑕佺紪閫犵瓟妗堬紝涔熶笉瑕佹彁浜ゅ钩鍙颁慨鏀广€?
- 鍚姏棰樺繀椤诲敖閲忚瘑鍒簩缁寸爜鍜岄煶棰戯紱璇嗗埆涓嶅嚭鏉ユ椂鏍囦负 `鍖呭惈鍚姏锛屼簩缁寸爜鎴栭煶棰戞棤娉曡瘑鍒玚銆?

## 鍙€夛細鐧惧害浜戠洏鍔熻兘

鐧惧害浜戠洏鐩稿叧鏂囦欢淇濈暀涓哄彲閫夊姛鑳斤紝涓嶅睘浜庝富娴佺▼蹇呴渶姝ラ锛?

- `cloud_link_uploader.py`
- `upload_to_cloud_link.bat`
- `tools/`
- `baidu_cookie.txt`
- `config.cloud.json`
- `config.cloud.example.json`

鍙湁鍦ㄩ渶瑕佹妸缁撴灉鏂囦欢涓婁紶骞剁敓鎴愬垎浜摼鎺ユ椂鎵嶄娇鐢ㄣ€備富娴佺▼瀹屾垚涓嶄緷璧栫櫨搴︿簯鐩樸€?

## 鏈€缁堥獙鏀?

```powershell
@'
import json
from pathlib import Path
from collections import Counter
res=json.loads(Path('_codex_review/results.json').read_text(encoding='utf-8-sig'))
print(Counter(v.get('status') for v in res.values()))
print('pending', sum(1 for v in res.values() if v.get('status')=='寰呰瑙夊鏍?))
print('total', len(res))
j=json.loads(Path('_codex_review/platform_modifications.json').read_text(encoding='utf-8'))
print(Counter(v.get('status') for v in j.values()))
'@ | .\.venv\Scripts\python.exe -
```

鍚堟牸鏍囧噯锛?

- `total` 绛変簬 URL 鎬绘暟銆?
- `寰呰瑙夊鏍竊 蹇呴』涓?0銆?
- `questions.xlsx` 宸插啓鍥炪€?
- 姣忔潯 `鏈夐敊璇紝宸蹭慨鏀筦 閮芥湁涓斿彧鏈?1 寮犲钩鍙板師閿欒绛旀鎴浘銆?
- `_codex_review/platform_modifications.json` 涓病鏈?`failed`銆?
