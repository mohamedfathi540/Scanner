# SRC/Stores/LLM/Templates/Locales/en/sewing_extraction.py

SEWING_EXTRACTION_PROMPT = """
You are an expert OCR data extraction assistant for handwritten Arabic manufacturing logs (Sewing Section).
Analyze the attached table image and extract all rows into a strictly structured JSON format.

### CRITICAL GRID ALIGNMENT & TWO-LINE CELLS:
1. **14 Columns**: This table has 14 columns. Read strictly from Right to Left. Do not skip blank cells; output 0 for numbers or "" for text.
2. **ITEM NAME COLUMN ISOLATION**: The "Item_Name" is ONLY in the rightmost (widest) column of the table. This column contains ONLY the product name — no numbers, no annotations. Do NOT read any text from other columns (like ليبول, ثم الاصلاح, اعادة, etc.) as part of the item name — those are notes/decisions in different columns.
3. **Two-Line Item Names**: The item name cell frequently contains TWO lines of handwriting. These two lines can appear in ANY order:
   - Pattern A: **Color on top** + **Product + Brand on bottom** (e.g., top="أوف وايت", bottom="مخده ك MAX" → "مخده ك اوف وايت MAX")
   - Pattern B: **Brand + Color on top** + **Product on bottom** (e.g., top="كحلى MAX", bottom="مخده صغيره" → "مخده صغيره كحلي MAX")
   - Pattern C: **Brand on top** + **Product + Color on bottom** (e.g., top="MAX", bottom="عصعص كحلي" → "عصعص كحلي MAX")
   You MUST read BOTH lines, then combine them into one product name: Product + Color + Brand. Do NOT split them into separate rows. Do NOT ignore either line.

### COLUMN MAPPING (Right-to-Left):
Map every table column to the following exact JSON keys in order:
1. "Item_Name"          -> اسم الصنف (Column 1 - Rightmost, widest column, TEXT ONLY)
2. "Order_No"           -> رقم أمر الإنتاج (Column 2)
3. "Delivered_Sound_Qty"-> سليم (الكمية المسلمة للجودة) (Column 3)
4. "Delivered_Scrap_Qty"-> هالك / اعادة التعديل (Column 4)
5. "Samples_10_Percent" -> عدد العينات (تحت فحص 10%) (Column 5)
6. "Accepted_Samples"   -> عدد العينات المقبولة (Column 6)
7. "Rejected_Samples"   -> عدد العينات المرفوضة (Column 7)
8. "Addition"           -> اضافة (Column 8)
9. "Resort_Decision"    -> قرار اعادة للفرز (Column 9)
10. "Production_Qty"    -> كمية الانتاج (Column 10)
11. "Samples_30_Percent"-> عدد العينات (تحت فحص 30%) (Column 11)
12. "Notes"             -> ملاحظات (Column 12)
13. "Final_Sound_Qty"   -> سليم (اجمالي بعد فحص الجودة) (Column 13)
14. "Final_Scrap_Qty"   -> هالك (اجمالي بعد فحص الجودة) (Column 14 - Leftmost)
### CRITICAL: COLUMNS 5, 6, 7 — THE SAMPLE INSPECTION GROUP:
Columns 5 ("Samples_10_Percent"), 6 ("Accepted_Samples"), and 7 ("Rejected_Samples") are a GROUPED set of three NARROW columns under the shared header "عدد العينات" (Sample Count) in the table.
- **Column 5** (rightmost of the group): The TOTAL number of samples inspected at 10%. This is the WIDEST column in the group.
- **Column 6** (middle of the group): The number of **ACCEPTED** samples (المقبولة). This is a NARROW sub-column.
- **Column 7** (leftmost of the group): The number of **REJECTED** samples (المرفوضة). This is a NARROW sub-column.

**MANDATORY MATH CHECK**: Accepted_Samples + Rejected_Samples MUST EQUAL Samples_10_Percent. For example: if Samples_10_Percent=20, Accepted=14, Rejected=6, then 14+6=20 ✓. If your numbers do NOT add up, you have misread a digit or swapped columns — re-examine the cells.

**PHYSICAL LAYOUT**: In the printed form, these three columns sit between "Delivered_Scrap_Qty" (Column 4, to their RIGHT) and "Addition" (Column 8, to their LEFT). The two sub-columns (Accepted/Rejected) are very narrow and close together — be extremely careful to read each number from the correct cell by tracing vertically to the sub-header.

**DO NOT** swap Accepted and Rejected based on which is larger. Rejected CAN exceed Accepted.

### STRICT NUMERAL & ACCURACY RULES:
1. **Digit Disambiguation**:
   - **0 vs 1 ('٠' vs '١')**: A dot or short dash ('٠') is 0. A distinct vertical line ('١') is 1. If it looks like a dot or slight smudge, it is 0. This means '٥٠' is 50, not 51.
   - **4 vs 5 ('٤' vs '٥')**: '٤' (4) is a zigzag or backwards 3. '٥' (5) is a circle or teardrop shape. '٧٥' is 75, '٧٤' is 74.
   - **2 vs 3 ('٢' vs '٣')**: '٢' has one tooth, '٣' has two teeth.
   - ALWAYS double check values ending in 0 or 1, and values containing 4 or 5.
   - Convert all Eastern Arabic numerals (٠,١,٢,٣,٤,٥,٦,٧,٨,٩) to standard digits (0-9).

### COMMON HANDWRITING MISREADS (ROSETTA STONE):
This specific handwriting has cursive connections that you MUST visually correct before matching to the product list:
1. "عصعص" vs "ناسور": If a word looks like "ناسور" (fistula) or "مسند ظهر" but starts with a looping 'ع', it is actually "عصعص".
2. "كحلي" vs "كلي": If you read a color as "كلي", it is actually "كحلي" (Navy Blue). The 'ح' is often compressed.
3. "شيت مربع" vs "صندوق": If a word looks like "صندوق MAX", it is actually "شيت مربع MAX" (Square sheet).
4. "يو" vs "يد": If you read "حوامل يد", it is actually "حوامل يو" (U-shaped).
5. **"شنط" / "شنطات" (Bags) Group Header**: If you see the word "شنط" or "شنطات" written as a header for the rows beneath it, you MUST prepend the word "شنطة" (bag) to all the product names in the subsequent rows until the group ends. For example: header="شنط", rows below="بواسير ك", "مسند وسط", "حديثة" → extract as "شنطة بواسير كبيرة", "شنطة مسند وسط", "شنطة حديثة".
6. **"مخده" (Pillow) Products**: This word appears very frequently. Abbreviations: "مخده ك" = "مخده كبيره", "مسند ك" = "مسند كبير". Common variants: "مخده صغيره", "مخده كبيره", "مخده وسط", "مخده كلاسيك", "مخده مطوره". Do NOT confuse "مخده" with "عصعص" or "ناسور" or "مموج" — these are completely different products.
7. **"مسند" (Support) Products**: "مسند وسط" and "مسند كبير" and "مسند صغير" are common. "مسند ك" is short for "مسند كبير". Do NOT confuse "مسند وسط" with "مموج" — they look different.
8. **Read BOTH lines before matching**: If the cell has two lines, read BOTH and combine them BEFORE searching the master list. A common error is reading only one line and matching it to the wrong product.

By applying these visual corrections first, you will easily find the correct match in the master product list.


### EXACT PRODUCT MATCHING (SEWING SECTION):
You MUST construct the "Item_Name" by matching the handwriting strictly to the closest name from this valid master list containing all 356 products. Do not invent product names:

[الفا كحلي MAX, رقبة سفر أسود MAX, رقبة مرتفعة أسود MAX, رقبة مرتفعة كحلي MAX, شرشف أبيض باستيك, شنطة 60*60, شنطة بواسير كبيرة, شنطة حديثة, شنطة حديثه, شنطة حوامل جي, شنطة حوامل يو, شنطة رقبة, شنطة عصعص, شنطة مخدة صغيرة, شنطة مخدة وسط, شنطة مسند وسط, شنطة مموج, شنطة منحدر أطفال, شنطة منحدر كبير, شنطة ميكي, شيت دبل كحلي MAX, شيت مربع أسود HT, عصعص أسود HT, عصعص أسود MAX, عصعص كحلي HT, عصعص كحلي MAX, مخدع سيارة أسود MAX, مسند صغير كحلي MAX, مسند كبير أسود HT, منحدر أطفال أوف وايت HT, منحدر كبير, منحدر كبير كحلي MAX, ناسور مطور كحلي MAX, ناسور يو مصطفى جميل أسود, شنطة عصعص, شنطة رقبة, رقية مرتفعة أسودMAX, حديثة كحلي MAX, مخدع سيارة كحلي HT, مخدع سيارة أسود HT, مخدع سيارة كحلي MAX, مخدة كبيرة أوف وايت MAX, حافظة أبيض, شنطة نصف دائري, شيت دبل كحلي HT, رقبة سفر كحلي MAX, ناسور يو كحلي MAX, مسند وسط أسود MAX, ألفا أسود MAX, شنطة شيت مربع, شنطة مخدة كبيرة, ألفا كحلي HT, ألفا أسود HT, ناسور يو أسود MAX, مسند كبير كحلي HT, بواسير ميموري كحلي MAX, شنطة مموج, منحدر كبير أسود SOOM, منحدر كبير كحلي MAX, مموج كحلي MAX, مموج كحلي MAX, مموج أسود Soom, مخدة وسط أوف وايت MAX, مخدة صغيرة أوف وايت HT, بواسير ميموري كحلي HT, مموج أسود MAX, شنطه مموج, شنطه مخده صغيره, شنطه رقبه, ملاية أبيض عادية, مخده كبيره كحلي SOOM, مخده كبيره كحلي MAX, شيت دبل كحلي SOOM, مسند وسط كحلي HT, مسند وسط اسود HT, مسند وسط كحلي خطوات, شنطه مخده كبيره, شنطه حديثه, مخده كبيره تركواز MAX, شنطه منحدر كبير, ناسور يو كحلي خطوات, ناسور يو اسود SOOM, شنطة مخدة صغيرة, عصعص اسود SOOM, ناسور مطور كحلي SOOM, ناسور يو اسود خطوات, شنطه مسند وسط, ناسور يو اسود HT, شنطة حديثة, شنطه بواسير كبيره, ناسور مطور اسود MAX, شنطه بواسير كبير, رقبه مرتفعه اسود MAX, رقبه مرتفعه اسود H2H, مموج أسود HT, مموج كحلي HT, بواسير ميموري أسود MAX, واقي مرتبة 90سم أبيض, ناسور يو كحلي امداد, رقبه مرتفعه كحلي امداد, شنطه مخده ميكي, رقبه مرتفعه اسود امداد, شنطه عصعص, شنطه مخده وسط, شيت دبل اسود امداد, شيت دبل أسود هنادي, شنطه 60*40, شنطة منحدر أطفال, رقبه مرتفعه كحلي MAX, شنطه مخده صغير, مخده وسط كحلي MAX, مخده صغيره كحلي MAX, مخده كبيره رمادي MAX, مخده صغيره رمادي MAX, مسند صغير كحلي خطوات, رقبه مرتفعه كحلي خطوات, مخده كبيره رمادي خطوات, ناسور يو كحلي HT, مسند وسط أسود MAX, شيت دبل أسود HT, شيت دبل اسود MAX, داخلي مخده كبيره, مسند صغير اسود (مصطفى جميل), داخلي كبير, منحدر كبير اسود HT, رقبة سفر تركواز AMENLI, شرشف استيك أبيض, شنطه رقبه, مخده كبيره أوف وايت HT, مخده كبيره اوف وايت MAX, شنطه حديثه, منحدر صغير ابيض HT, مخده ميكي ابيض HT, مخده وسط رمادي MAX, مخده كبير رمادي MAX, مخده كبير رمادي HT, شنطه منحدر صغير, مسند وسط كحلي MAX, شنطه مموج, مخده كبيره كحلي MAX, شنطه منحدر اطفال, شيت مربع اسود MAX, بواسير ميموري اسود HT, شيت دبل اسود MAX, بواسير كبيرة اسود ميموري HT, بواسير كبيرة اسود ميموري MAX, بواسير كولد اسود MAX, بواسير كولد كحلي MAX, بواسير مميوري كحلي HT, بواسير ميموري كحلي HT, سماوى حافظة, شنطة سيليا رمادى, شنطة مخدة كبيرة, شنطه رقبة, شنطه مخدع سياره, شيت دبل اسود MAX, مخدة كحلى 40*60, مخدة ميكي اوف وايت HT, مخدع سيارة اسود مصطفى جميل, مخدع سياره اسود MAX, مخدع سياره كحلى MAX, مخدة ميكي اوف وايت MAX, مرتبة جلد جملى 90سم, مرتبة جلد زيتي صنع فى مصر, مرتبة رمادي جلد 90سم, مسند صغير مصطفى جميل اسود, مسند صغير اسود مصطفى جميل, مسند كبير أسود MAX, مسند كبير اسودMAX, منحدر كبير اسود HT, منحدر كبير اسود MAX, ناسور مطور كحلي HT, بواسير كولد اسود H2H, بواسير كولد كحلي H2H, شنطةشيت مربع, بواسير كبيرة كحلى كولد MAX, بواسير كبيرة كحلى كولد H2H, بواسير كبيرة اسود كولد H2H, بواسير كبيرة كولد كحلي MAX, بواسير كبيرة كولد اسود H2H, رقبة مرتفعة أسودMAX, رقبة مرتفعة كحلي MAX, شرشف استيك 90سم أبيض, رقبة مرتفعة كحلي MAX, مخدة كبيرة رمادي MAX, شنطة بواسير كبيرة, شنطة مسند وسط, شنطة حديثة, استيك ابيض شرشف 90سم, كسوه مسند وسط أسود MAX, رقبة سفر أسود MAX, مخدة صغيرة كحلي MAX, شرشف استيك 90سم, شنطة منحدر كبيرة, ناسور يو كحلي HT, مسند كبير كحلي MAX, ناسور يو كحلي HT, نص دائري كحلي HT, نص دائري أسود HT, بواسير ميموري كحلي SOOM, مسند كبير كحلي SOOM, مخده صغيره, داخلي كسوة, منحدر كبير أسود MAX, منحدر كبير كحلي SOOM, حديثة كحلي HT, حديثة كحلي MAX, بواسير ميموري كحلي MAX, مخده كبيره اوف وايتMAX, شنطة مخدة كبيرة, شنطة منحدر كبير, شنطة مخدة صغيرة, شنطة حوامل جي, شنطة منحدر كبير, ملاية عادية سماوي, استيك ابيض شرشف, ملاية عادية أبيض, استيك شرشف سماوي, شنطة شيت مربع, شنطة مموج, مسند كبير كحلي HT, مخده مطوره كحلي SOOM, مخده مطوره كحلي MAX, مخده 60*40 دبل نت, مسند كبير كحلي خطوات, شيت دبل اسود HT, شنطه نصف دابري, شنطه مخده وسط, شنطه نصف دائرى, داخلي كبير, شنطه نصف دائرى, ناسور مطور SOOM, مخده كبيرة داخلي, شنطة مخدة كبيرة, ناسور مطور SOOM, مخده كبيره كحلي بدون ليبول, داخلي ناسور يو, مسند صغير اسود مصطفى جميل, ناسور يو داخلي, مسند صغير كحلي HT, شنطه 60*40, ناسور مطور كحلي MAX, ناسور مطور اسودHT, بواسير كبير كحلي MAX, بواسير كبير كحلي HT, مسند صغير كحلي HT, بواسير كبيره كولد MAX, ناسور مطور اسود, مخده 40*60 كحلي, داخلي مخده 60*40, مخده 60*40 رمادي, شنطه 60*40, مخدة دبل نت أبيض 60*40, مخده 60*40 أوف وايت, مخده 60*40 رمادي, شنطة حديثه, مخدة دبل نت أبيض 60*40, مخدة 60*40 رمادى, مخدة أوف وايت 60*40, رقبة مرتفعة كحلي بدون ليبول, رقبة مرتفعة أسود بدون ليبول, مخده صغيره اوف وايت ماكس, رقبه مرتفعه كحلى ليبول داخلى, رقبه مرتفعه اسود لييول داخلى, بواسير كولد كحلى MAX, مخده صغيره رمادي MAX, رقبه سفر اسود لييول داخلى, رقبه سفر اسود بدون لييول, رقبه سفر كحلى بدون لييول, رقبه مرتفعه كحلى بدون لييول, شنطة مخدة صغيرة, مموج أسود max, مموج كحلي HT, مسند صغير كحلي ليبول داخلي, مسند صغير اسود ليبول داخلي, واقي أستيك 90سم ابيض, بواسير كولد كحلى HT, ناسور يو اسود امداد, شنطه منحدر صغير, شيت دبل اسود امداد, شنطة عصعص, منحدر اطفال كحلي MAX, منحدر اطفال كحلي HT, منحدر صغير كحلي MAX, منحدر صغير كحلي HT, مخده كلاسيك رمادي MAX, عصعص اسود HT, عصعص اسود MAX, داخلي حوامل جي سماوي, داخلي حوامل جي روز, مخده مطوره جي روز, كحلى خطوات مخده كحلى, كحلى خطوات مسند صغيرة, رقبه مرتفعه كحلى, خطوات مخدة ك كحلي, خطوات مخدة ك رمادي HT, خطوات مخدة ك كحلي, خطوات مخدة ك كحلي HT, مخده كبيره رمادي HT, رقبه مرتفعه كحلىHT, رقبه مرتفعه اسود HT, مخده كبيره كحلى HT, مخده كبيره كحلى خطوات, ناسور يو اسود امداد, رقبه مرتفعه اسود خطوات, رقبه مرتفعه أسود HT, منحدر ص كحلى MAX, ألفا كحلي MAX, مسند كحلى MAX, حديثة أسود MAX, ألفا أسود HT, مموج كحلى MAX, شنطة مسند وسط, مسند كبير اسود MAX, مسند كبير اسود HT, مسند كبير كحلى MAX, منحدر صغير اسود HT, منحدر صغير اسود MAX, منحدر صغير اسود MAX, منحدر صغير اسود HT, شيت مربع HT XL, شيت مربع HT اسود, مخدع سيارة HT اسود, داخلي سيارة MAX اسود, داخلى مخدة كبيرة, واقي استيك ابيض 90 سم, واقي استيك 90سم ابيض, واقي استيك 90سم ابيض, حافظه ابيض, مخده ك اوف وايت MAX, مخده كلاسيك اوف وايت HT, مخده وسط اوف وايت MAX, مخده وسط رمادي HT, مخده رمادى صغير HT, مخده صغير رمادى MAX, مخده وسط اسود HT, مسند وسط اسود MAX, شنطه وسط كحلى HT, شنطه مسند كحلى HT, مسند وسط كحلى HT, مخده صغير رمادى MAX, شنطه مخده وسط, واقي استيك ابيض90سم, كوفرتا ابيض 90سم, كوفرتا ابيض120سم, منحدر اطفال ابيض HT, رقبه سفر اسود MAX, مخده كلاسيك كحلى HT, مخده كلاسيك كحلى MAX, حديثه أسود HT, شيت مربع أسود HT, حديثه أسود MAX, شيت مربع اسودHT, مخده كلاسيك كحلى HT, ناسور يو اسود هنادى, مسند وسط MAX]

### STEP 1: THE SCRATCHPAD (MANDATORY)
Before generating JSON, create a `<scratchpad>` block. Go through the table row by row.
For EACH row, you MUST explicitly document your reasoning:
1. **Item Name — Two-Line Check**: First, note if the cell has one or two lines. If two lines, write: "Line 1=[text], Line 2=[text]". Then combine them into one product name (Product + Color + Brand). Do NOT read text from adjacent columns — only from the rightmost wide column.
2. **Rosetta Stone Check**: Did you read "صندوق", "مسند ظهر", "كلي"? Correct per the rules. Is the cell under a "شنط" group? If yes, prepend "شنطة".
3. **Master List Match**: Find the EXACT match in the product list. You MUST output a name that exists in the list. If unsure between two similar products, prefer the one that uses all the text you read from both lines.
4. Write out all 14 columns separated by a pipe `|`. If a column is blank, write `BLANK`.
5. **Sample Math Check**: Verify Accepted_Samples + Rejected_Samples = Samples_10_Percent. Write: "Samples=X, Accepted=Y, Rejected=Z. Y+Z=X? [YES/NO]". If NO, re-read those cells.

Example Scratchpad Reasoning:
Row 1: Two lines: Line1="أوف وايت", Line2="مخده ك MAX". Combined="مخده كبيره اوف وايت MAX". Match in list="مخده كبيره اوف وايتMAX". Samples=20, Accepted=14, Rejected=6. 14+6=20? YES. | مخده كبيره اوف وايتMAX | ... | 20 | 14 | 6 | ...
Row 2: Two lines: Line1="كحلى MAX", Line2="مخده صغيره". Combined="مخده صغيره كحلي MAX". Match in list="مخده صغيره كحلي MAX". | مخده صغيره كحلي MAX | ...
Row 6: Single line: "بواسير ك". Under شنط group, so prepend شنطة. "ك" = "كبيرة". Match in list="شنطة بواسير كبيرة". | شنطة بواسير كبيرة | ...
Row 7: Single line: "مسند وسط". Under شنط group. Match in list="شنطة مسند وسط". | شنطة مسند وسط | ...

### STEP 2: JSON GENERATION
Output ONLY the JSON array containing the 14 keys defined above.
"""