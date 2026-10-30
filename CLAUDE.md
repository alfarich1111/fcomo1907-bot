# Project notes

Before writing any caption for CHELSEA UZ (@CHELSI_CHELSEAUZ_CFCUZ), read `data/emoji_guide_chelsea.md` and follow it.
It overrides any shorter emoji list in a task. Many stickers show a real face or logo, so never put one next to a different person, club or outlet.

# Post photos (both channels: CHELSEA UZ and @FComo1907)

The owner wants new, high-quality photos on every post. Follow this whenever you choose a photo:

- New: from the story itself, or from this season. The current kit, the current squad. No old photos when a recent one exists. Don't reuse a photo from the channel's recent posts.
- Quality: sharp, not stretched or heavily compressed. Get the largest version: on chelseafc.com images (res.cloudinary.com/chelsea-production) use c_fit,h_2000,w_3000,f_jpg, and elsewhere remove resize parameters such as ?w=, ?width=, ?resize= from the image URL.
- Run `python photo_check.py <file>` on the downloaded file. If it says LOW, look for a better photo in other articles on the same story (club site, ESPN, BBC, Sky Sports, agencies). Use a LOW photo only if nothing better exists after trying at least 3 sources, and say so in your report.
- Look at it before posting. It must fit the story and show the right person or club. Reject watermarks, other channels' logos, finished graphics or posters with text, screenshots, collages, and photos with the opponent as the main subject of a Chelsea or Como story.
