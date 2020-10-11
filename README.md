# pixiv_rank_web_crawler
this web crawler can search the daily rank of the pixiv, get the target imgs info and download with your given keyword 
## guidance
- step 1: download chromedriver from [link](https://sites.google.com/a/chromium.org/chromedriver/downloads), pay attention to **your chrome version**, download corresponding version
- step 2: run PixivRankGUI.py
- step 3: choose the location of your chromedriver
- step 4: insert in your tags, **Chinese tag** is the best, you can repeatably add tags and view them by button **check added tags** 
- step 5: choose the ranking range in which you do the search, for example, put in 100 means searching your targeted images in **top-100** ranking lists
- step 6: choose the number of multi-thread, the max num is 24
- step 7: you can choose targeted rank list by choose **search mode** listbox, choice modes are as follows:
> daily 日排行
> weekly 周排行
> monthly 月排行
> rookie 新人排行
> original 原创排行
> male 最受男性喜爱排行
> female 最受女性喜爱排行
- step 8: execute web crawler:
> 1. Button **run**: search for targeted images
> 2. Button **results**: write info of targeted images into **./PixivImage/results.csv**
> 3. Button **save**: save targeted images into **./PixivImage** folder
## attetion
It's OK to find a chrome page is opened when click **Button run**, just ignore it.