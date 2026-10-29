# Process of solving challenge 3

## 1. Data exploration
I started out with checking the more obvious data issues in the manufacturer names and the model names:
 - Typos: STRKYER MEDICAL, COVIDEN, PHILLIPS MEDICAL.
 - Spacing and hyphens: MID MARK / MIDMARK, WELCH ALLYN / WELCH-ALLYN / WELCHALLYN.
 - Legal suffixes: ZOLL / ZOLL MEDICAL CORP / ZOLL MEDICAL CORPORATION.
 - Abbreviations and legal names: GE, G.E., GENERAL ELECTRIC, and MINNESOTA MINING AND MANUFACTURING (3M’s legal name).
 - Old or parent names: DATEX-OHMEDA, GE DATEX OHMEDA, HILLROM WELCH ALLYN, KONINKLIJKE PHILIPS.
 - Word order: STORZ KARL.
 - Model variants: R SERIES / R-SERIES / RSERIES, TAT 5000 / TAT-5000 / TAT5000, MEDFUSION3500.

These were the easier rules I decided to keep in a running rule book so that I can ask Claude to check against them in the final alias dictionaries.

## 2. Normalization
1. Rule-based cleanup (case, punctuation, legal suffixes): Dropped as too brittle for the given task. These are prominent in the model names with spaces and '-' being the major differentiators in the models. But, just doing case/punctuation wouldn't look at the more intricate and complex mutations in the data meant I had to drop this for being too simple.
2. Similarity clustering: In this, I used the SequenceMatcher method from difflib. This uses a modified version of the "Gestalt Pattern Matching" algorithm to find the longest contiguous matching subsequences recursviely. This did not result in good output either, where it was producing false chains (ACIST, OEC, GE MEDICAL SYSTEMS) through the shared ‘MEDICAL SYSTEMS’ tokens”.Going through all of them would've been difficult so I decided to drop this method.
3. First-word grouping: I noticed that almost all companies have distinct first words and that can be a good signal to try to cluster together manufacturers. This was used as a starting point for hand-reviewing. This method is known for over and under merges so I had to be careful.
4. Model based reverse clustering (bridge): group manufacturer spellings by shared model string. Shared models have the added benefit of detecting companies which have abbreviations and couldn't be caught with the earlier methods. 119 models and 146 spellings were reviewed by hand in a drag-and-drop tool Claude built [Alias Buckets](https://claude.ai/artifact/VAZ7sj2cLVa9ruKJgz2Qw1). This step took about 15-20 minutes.

    - The artifact is a small review tool which loads the model based clustering csv and then each model will show all the manufacturers tagged to it. All I had to do was drag and drop each manufacturer either into a new bucket (if this manufacturer didn't exist) or into an existing bucket. I Googled a few similar looking companies to check if they were subsidiaries or partner companies and stacked all under one spelling which was a part of the medical institution records.
5. The bridge covered 71% of the records. Out of the remaining spellings for manufacturers, I did the first word grouping and used that to bucket a few other which had the same first token. This took the coverage to 77%. After this all other manufacturers were single spelling so they became their own buckets.
6. I turned my attention to the model names now, and found that the data issues were within a few mutants:
    - Space between the names (MX40 vs MX 40)
    - '-' between the names (MX-40 vs MX 40)
    - Sign instead of wording (SURE TEMP + vs SURE TEMP PLUS)
7. I picked out all the model names for a single manufacturer which had model spellings that match once case, spaces and punctuations are ignored (Match 1). Next, near-identical long models (8 or more characters, atleast 90% similar) that contain same digits (Match 2). About 95 spellings were reviewed by hand. This took about 20 minutes.
8. All of this results in two files, manufacturer_alias and model_name_alias which are then used to create the final payload dictionary.

## Cross Source mapping
Since each manufacturer and model_name came with the origin in the review artifact, I knew that the actual spelling has to be chosen amongst the medical institution ones.
 - After the maps were applied, every Partner device was checked for a health-system match.
 - At one point 11 didn’t match, and I fixed seven by hand (MX40, ALARIS 8100, ALARIS PUMP MODULE 8100, LIFEPAK CR+, MEDFUSION 3500 SYRINGE PUMP, S3 MED/SURG BED, 690 SURETEMP).
 - Then the 3M legal name gap (Minnesota Mining and Manufacturing Company), LP CR PLUS and the MEDTRONIC / PHYSIO CONTROL merge turned up.
 - Final result: all 107 Partner devices match.

## External sources:
 - I used Claude code to write analysis code, propose various ways to run exploration and then with my idea of the reverse model based clustering I asked it to write code for the creation of that data feed for the review tool. I also kept a rule book, which Claude then used during the final checks of the entire data before submission.
 - All the code output by Claude Code was hand checked by me before using, so I knew what it was doing and making sure there were no hallucinations.

 ## Reproducibility
 - Since this piece of work had a few custom modules, reproducing the final dictionary depends on the alias files I have created. These files and all other source code is present on my [github repo](https://github.com/Raphaeal19/equiply-hiring-2).


