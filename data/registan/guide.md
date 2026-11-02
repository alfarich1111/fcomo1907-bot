# Registan LC | Nukus filiali (@registan_nukus): how to adapt posts from other branches

The owner's rule: posts come only from the other Registan branches (`python registan_feed.py`), rewritten for Nukus, in Karakalpak only.

## Which posts may be used
Only material that is true for any reader in Nukus and for any branch:
- Quote graphics with the Registon logo and no branch name, like a famous person's quote on orange with a translation. The owner especially wants these translated and posted. Prefer them.
- Lessons: English words and idioms, grammar, maths or language tips
- Study advice, time planning, motivation
- Advice for parents
- A question or riddle for the comments
- General facts about Registan or national exams that don't depend on a branch

Think about each post first: would it be true and useful for a reader in Nukus? If it's about one particular branch, don't use it. The owner: post it only if it fits Registan Nukus.

## Never use these
They would tell Nukus readers something false:
- Another branch's teachers, managers, students, results, certificates or photo reports
- Dates, times, prices, addresses, phones, links, bots or sign-up details of another branch
- Events, olympiad stages, mock exams, free lessons, new groups, holidays or discounts
- Anything naming a city or district other than Nukus, or «eng kuchli ustozlar» type claims about Nukus
- Students' personal data, certificates or children's faces
- Answer keys or tests whose file is only in the other channel

If a post looks network-wide and useful (for example an exam for all branches) but needs a date, price or place, don't publish it. Tell the owner in your report.
Don't invent facts about the Nukus branch: its teachers, prices, groups, results or schedule.

## Karakalpak
Write in Karakalpak Latin only, with correct letters: á, ǵ, ı, ń, ó, ú. Rewrite naturally, not word for word. Read the channel's latest posts first and use their vocabulary:
«oqıw orayı», «oqıwshılar», «ustaz», «perzentińiz», «Menedjerler menen baylanısıw», «Kommentke jazıp ketiń», «Házir jazılıń».
If you aren't sure a sentence is correct Karakalpak, rewrite it more simply. English examples in a lesson stay in English.
Use the name «Registan oqıw orayı».

## Format
Short: 1 to 4 short paragraphs with an empty line between them. One or two normal emoji at most on the first line. No hashtags.
End every post with exactly:

📞 Menedjerler menen baylanısıw:
📲 @Registan_menejer_Nukus
+998 77 446 2700

## Photo
Telegram photo URLs from the branch feed may be used only if the picture has no other branch's name, phone or address, no people from that branch, and no text about a date or price. The general logo «REGISTON O'QUV MARKAZI» with no branch name is fine; leave it as it is. LOOK at it first. If none is clean, post text only. Never edit another branch's name out of a picture. Don't reuse a photo the channel used recently.

## Text inside pictures
Uzbek or Russian text in a picture must become Karakalpak. English quotes and names stay. Download the picture and replace each text block:

python registan_patch.py work/in.jpg outbox/$TS.jpg --patch "x0,y0,x1,y1|font size|weight|new text" --patch ...

Each box must cover the old text exactly, on plain or gradient background only, with the same background 6 px outside every side. Use the old text's left edge and about its font size; weight is 400 for normal and 700 for bold. LOOK at the result: no old letters left, no visible patch, nothing cut off, no text outside its card. Correct the coordinates and try again. If text sits on a photo, or the picture still looks wrong, don't use the picture: post its content as text only.

Use `"photo": "outbox/$TS.jpg"` in the outbox file, and add a short Karakalpak caption above the contact lines. Keep names, dates and sources in the picture as the branch gave them.

## No repeats
Read `python recent_web.py 200 registan_nukus` first. Don't publish a topic or tip the channel already has in that list.
