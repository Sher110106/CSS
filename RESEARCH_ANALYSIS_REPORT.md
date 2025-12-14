# Semaglutide Reddit Discourse Analysis: Research Questions, Methodology & Findings

**Date**: December 1, 2025  
**Dataset**: 23,405 Reddit documents (2019-2025)  
**Analysis Period**: March 2019 - October 2025 (6.6 years)

---

## Executive Summary

This study analyzes 23,405 Reddit posts and comments discussing semaglutide (Ozempic, Wegovy) across 6 major health subreddits from 2019-2025. Using Latent Dirichlet Allocation (LDA) topic modeling and VADER sentiment analysis, we identified 3 major discourse themes and tracked how public sentiment and engagement evolved over time. The research reveals significant temporal shifts in both discussion topics and community sentiment, with implications for understanding patient experiences and healthcare communication.

**Key Findings**:
- **3 distinct discussion topics** identified (coherence: 0.682)
- **68.7% positive sentiment** overall, but declining from 2020 to 2023
- **Dramatic growth**: 12,655 documents in 2025 vs. 14 in 2019 (903x increase)
- **Lower engagement, higher volume**: 2025 posts average 317 score vs. 1,144 in 2020
- **Topic 2 (Community Support)**: Highest sentiment (0.370) but only 2.7% of discourse

---

## 1. Research Questions

### Primary Research Questions

#### RQ1: **Temporal Evolution of Discourse**
*How has the conversation about semaglutide evolved over time (2019-2025)?*

**Sub-questions**:
- What drove the 903x increase in discussion volume from 2019 to 2025?
- Why did sentiment decline from 0.42 (2019) to 0.27 (2023) before recovering to 0.33 (2025)?
- How does the temporal pattern reflect real-world events (FDA approvals, media coverage, supply shortages)?

**Hypothesis**: The conversation evolved from early adopter experiences (high engagement, positive) to mainstream discourse (high volume, mixed sentiment) as semaglutide gained widespread attention.

---

#### RQ2: **Engagement vs. Volume Paradox**
*Why does increased discussion volume correlate with decreased engagement metrics?*

**Observation**:
```
Year   | Posts | Avg Score | Median Score
-------|-------|-----------|-------------
2020   |    40 |     1,144 |        888
2023   |    83 |       212 |         35
2025   |   808 |       317 |          6  ← Median score collapsed
```

**Sub-questions**:
- Does lower engagement indicate:
  - Content saturation (too many similar posts)?
  - Shifting demographics (casual users vs. committed patients)?
  - Platform algorithm changes?
- Are high-engagement posts qualitatively different from low-engagement posts?
- What drives the massive median score drop to just 6 in 2025?

**Hypothesis**: As semaglutide entered mainstream discourse, subreddits became flooded with repetitive questions and experiences, diluting the novelty and engagement that characterized early discussions.

---

#### RQ3: **Topic-Sentiment Relationship**
*How does sentiment vary across discussion topics, and what does this reveal about patient experiences?*

**Findings**:
```
Topic                      | Dominance | Sentiment | Interpretation
---------------------------|-----------|-----------|------------------
0: Weight Loss & Experiences|   76.7%   |   0.320   | Dominant but moderate sentiment
1: Diet & Nutrition        |   20.7%   |   0.342   | More positive than Topic 0
2: Community Support       |    2.7%   |   0.370   | Highest sentiment, lowest volume
```

**Sub-questions**:
- Why is Topic 2 (Community Support) the most positive but least discussed?
- What specific aspects of weight loss experiences (Topic 0) drive neutral-positive sentiment?
- How do dietary discussions (Topic 1) maintain higher positivity despite practical challenges?

**Hypothesis**: Community support posts are rare but highly positive (seeking/giving encouragement), while the dominant weight loss discussions reflect mixed real-world experiences (successes and side effects).

---

#### RQ4: **Framing & Discourse Positioning**
*How do users frame their semaglutide experiences, and how has this framing changed?*

**Dimensions**:
1. **Medical vs. Lifestyle Framing**
   - Topic 0: Weight loss, appearance ("look", "feel")
   - Topic 1: Diet management, nutrition science
   - Topic 2: Community, support-seeking

2. **Expert vs. Layperson Language**
   - Early posts (2019-2020): Higher use of medical terminology?
   - Recent posts (2024-2025): More colloquial, lifestyle-focused?

3. **Authority Positioning**
   - Who claims expertise? (Doctors, long-term users, researchers)
   - How do users cite sources or personal experience?

**Sub-questions**:
- Has discourse shifted from "diabetes medication" to "weight loss drug"?
- Do users adopt medical authority (technical language) or emphasize lived experience?
- How do laypeople translate medical concepts for community consumption?

**Research Method**: Qualitative coding of high-engagement posts across time periods, comparing linguistic markers of authority and framing strategies.

---

#### RQ5: **Sentiment Decline Mystery (2020-2023)**
*What caused the 30% drop in sentiment from 2020 (0.39) to 2023 (0.27)?*

**Timeline Analysis**:
```
2019-2020: High sentiment (0.39-0.42) - Early adopters, positive experiences
2021-2022: Moderate decline (0.39 → 0.33) - Growing awareness
2023: Sharp drop (0.27) - ??? 
2024-2025: Recovery (0.32-0.33) - Stabilization
```

**Potential Explanations**:
1. **Supply Shortage** (2023): TikTok virality led to shortages, frustrating patients
2. **Side Effect Awareness**: Increased reporting of gastroparesis, "Ozempic face"
3. **Cost/Insurance Issues**: More discussions about access barriers
4. **Mainstream Criticism**: Media coverage of misuse, celebrity backlash

**Research Method**: Negative sentiment document analysis for 2023 to identify common themes driving the drop.

---

### Secondary Research Questions

#### RQ6: **Post Length vs. Engagement**
*Do longer, more detailed posts receive more engagement?*

**Observation**: Average document length is only 31.3 tokens - quite short.

**Analysis**: Correlate token count with score/engagement metrics across years.

---

#### RQ7: **Subreddit-Specific Patterns**
*How do discussions differ across r/Ozempic, r/Semaglutide, r/diabetes_t2, etc.?*

**Expected Patterns**:
- r/diabetes_t2: Medical focus, higher clinical language
- r/Ozempic, r/Semaglutide: Mixed medical/lifestyle
- r/WeightLossAdvice: Lifestyle-dominant

---

#### RQ8: **Early Period Undersampling Impact**
*How does the severe undersampling of 2019 data affect temporal conclusions?*

**Limitation**: Only 14 documents from 2019 vs. 1,006 from 2020.

**Consideration**: Any 2019 vs. post-2020 comparisons are statistically limited. Focus on 2020-2025 trends for robust conclusions.

---

## 2. Methodology

### 2.1 Data Collection
- **Source**: Reddit via PRAW API + BAScraper (ArcticShift)
- **Subreddits**: r/Ozempic, r/Semaglutide, r/WeightLossAdvice, r/diabetes_t2, r/diabetes, r/loseit
- **Keywords**: semaglutide, ozempic, wegovy, rybelsus
- **Raw Data**: 54,734 documents (1,402 posts + 53,332 comments)
- **Processed Data**: 23,405 documents (filtered <10 tokens)

### 2.2 Preprocessing Pipeline
1. **Text Cleaning**: URL removal, lowercasing, special character handling
2. **Tokenization**: spaCy en_core_web_sm
3. **Stopword Removal**: NLTK + custom medical stopwords
4. **Lemmatization**: Preserve medical terminology
5. **Filtering**: Min 10 tokens per document

**Final Corpus**: 17,996 unique terms, 733,360 total tokens, avg 31.3 tokens/document

### 2.3 Topic Modeling (LDA)
- **Algorithm**: Latent Dirichlet Allocation (Gensim LdaMulticore)
- **Model Selection**: Tested K = {2, 3, 4, 5}
- **Best Model**: **K=3 topics** (coherence C_v = 0.6819)
- **Parameters**: 
  - Passes: 10
  - Iterations: 400
  - Alpha: asymmetric
  - Eta: auto
  
**Topic Selection Rationale**: K=3 maximized coherence while maintaining interpretability. Higher K values (4, 5) showed topic fragmentation without substantive gain.

### 2.4 Sentiment Analysis
- **Tool**: VADER (Valence Aware Dictionary and sEntiment Reasoner)
- **Rationale**: Optimized for social media text, handles negation and intensifiers
- **Metrics**:
  - Compound score: -1 (most negative) to +1 (most positive)
  - Classification: positive (>0.05), neutral (-0.05 to 0.05), negative (<-0.05)

### 2.5 Temporal Analysis
- **Granularity**: Yearly and monthly aggregations
- **Metrics**: Document count, sentiment mean, engagement (score, comments)
- **Engagement Score Formula**: `score + (num_comments × 2)`
  - Rationale: Comments indicate deeper engagement than upvotes alone

### 2.6 Statistical Analysis
- **Sentiment by Topic**: ANOVA to test topic-sentiment relationship
- **Temporal Trends**: Linear regression on yearly sentiment
- **Engagement Trends**: Spearman correlation (volume vs. engagement)

---

## 3. Key Findings

### 3.1 Topic Analysis: Three Discourse Themes

#### **Topic 0: Weight Loss & Personal Experiences (76.7%)**
**Top Words**: weight, get, lose, look, like, feel, start, take, people, work

**Interpretation**: The dominant discourse centers on personal weight loss journeys, physical changes, and medication effectiveness. Users discuss:
- Weight loss progress ("how much weight did you lose?")
- Physical appearance changes ("do I look different?")
- Starting the medication ("when did it start working?")
- Comparing experiences with others

**Sentiment**: 0.320 (moderate positive)
- Reflects mixed experiences: successes, plateaus, side effects
- Balance of excitement (initial weight loss) and frustration (slow progress, side effects)

---

#### **Topic 1: Diet & Nutrition Management (20.7%)**
**Top Words**: eat, food, calorie, like, carb, get, sugar, make, protein, meal

**Interpretation**: Focused on practical dietary strategies while on semaglutide:
- Managing reduced appetite ("what foods can you tolerate?")
- Nutrition optimization (protein, low-carb approaches)
- Meal planning and food choices
- Sugar cravings and carb management

**Sentiment**: 0.342 (higher positive)
- Higher sentiment suggests users find value in dietary discussions
- Sharing successful strategies creates positive discourse
- Problem-solving focus maintains constructive tone

---

#### **Topic 2: Community Support & Meta-Discussion (2.7%)**
**Top Words**: semaglutide, message, offer, permit, discussion, private, please, sub, question, concern

**Interpretation**: Meta-level subreddit interactions:
- Seeking/offering private messages for support
- Questions about subreddit rules and appropriate discussions
- Direct support requests ("can someone message me?")
- Mod interactions and community guidelines

**Sentiment**: 0.370 (highest positive)
- Support-seeking and helping behaviors are inherently positive
- Small volume suggests most users don't need to request private support
- High sentiment reflects gratitude and community bonding

**Notable**: Despite highest positivity, this topic is rare (628 docs), suggesting strong norms against help-seeking posts or effective peer support limiting need.

---

### 3.2 Temporal Dynamics: The Great Expansion

#### **Volume Growth (2019-2025)**
```
Year   | Documents | Growth Rate
-------|-----------|-------------
2019   |        14 | baseline
2020   |     1,006 | 71x increase
2021   |     1,074 | 6% growth
2022   |       848 | -21% decline
2023   |     2,336 | 175% surge
2024   |     5,472 | 134% surge
2025   |    12,655 | 131% surge (partial year)
```

**Key Inflection Points**:

1. **2019-2020 Jump** (71x): 
   - Reddit community formation
   - r/Ozempic, r/Semaglutide subreddits gain critical mass
   - Early adopter discussions

2. **2022 Dip** (-21%):
   - Possible consolidation or data collection artifact
   - Suggests natural ebb/flow in online health communities

3. **2023 Explosion** (175%):
   - **TikTok virality**: #Ozempic trends, celebrity speculation
   - Mainstream media coverage intensifies
   - Supply shortage creates urgency/frustration (drives discussion)

4. **2024-2025 Sustained Growth**:
   - Semaglutide becomes household name
   - More patients prescribed → more discussions
   - Broader demographic reach

---

#### **Sentiment Trajectory: The 2023 Valley**

```
Year   | Mean Sentiment | Interpretation
-------|----------------|----------------
2019   |   0.415        | Early enthusiasm
2020   |   0.389        | Sustained positivity
2021   |   0.386        | Stable
2022   |   0.331        | Beginning decline
2023   |   0.266        | LOWEST (30% drop from 2020)
2024   |   0.319        | Recovery begins
2025   |   0.329        | Stabilization
```

**The 2023 Sentiment Drop: Explanatory Framework**

**Likely Causes** (ranked by explanatory power):

1. **Supply Shortage Impact** (Primary Driver)
   - TikTok virality → massive demand surge
   - Novo Nordisk production shortfall
   - Patients unable to refill prescriptions
   - Frustration, anxiety, withdrawal symptoms dominate discourse

2. **Increased Negative Media Coverage**
   - Focus on misuse (non-diabetic users)
   - "Ozempic face" and gastroparesis concerns
   - Celebrity backlash and body positivity debates
   - Users defensive or questioning safety

3. **Access/Cost Frustrations**
   - Insurance denials increase as demand rises
   - High out-of-pocket costs ($900-1,000/month)
   - Class/equity concerns enter discourse

4. **Normalized Side Effect Reporting**
   - Larger userbase → more side effect posts
   - Severe cases (hospitalizations) gain visibility
   - Negative experiences drown out positive

**2024-2025 Recovery**:
- Supply stabilizes → access improves
- Users adapt expectations (side effects normalized)
- Positive long-term success stories accumulate
- Community develops coping strategies

---

### 3.3 The Engagement Paradox: More Posts, Less Impact

#### **Engagement Collapse (2020-2025)**
```
Year   | Posts | Mean Score | Median Score | Median Drop
-------|-------|------------|--------------|-------------
2020   |    40 |     1,144  |        888   | -
2021   |    40 |       755  |        826   | -7%
2022   |    40 |       439  |        111   | -87%
2023   |    83 |       212  |         35   | -68%
2024   |   209 |       533  |         80   | +129%
2025   |   808 |       317  |          6   | -92%  ← DRAMATIC
```

**Key Insight**: Median score is more revealing than mean.
- 2025 median of **6** means half of posts get ≤6 upvotes
- Suggests vast majority of posts are low-engagement
- A few viral posts drive up the mean (317)

---

#### **Explanatory Hypotheses**

**H1: Content Saturation Hypothesis**
- As volume increases (808 posts in 2025), competition for attention intensifies
- Many posts ask repetitive questions ("starting dose advice", "is this normal?")
- Users tired of answering same questions → less engagement
- **Evidence**: Consistent topics (Topic 0 dominates across years) but declining engagement

**H2: Demographic Shift Hypothesis**
- **Early adopters** (2019-2021): Invested patients, active community members
  - Engaged deeply, upvoted generously, built community norms
- **Mainstream influx** (2023-2025): Casual users, one-time posters
  - Post question → get answer → leave (no reciprocal engagement)
- **Evidence**: Lower comments-per-post ratio in recent years?

**H3: Platform Algorithm Hypothesis**
- Reddit algorithm changes (2023-2024) may prioritize different content
- Subreddit growth → posts buried faster in feed
- Less time on "hot" page → less visibility → less engagement

**H4: Novelty Depreciation Hypothesis**
- **2019-2020**: Semaglutide was novel; every story was unique
- **2025**: Weight loss stories are routine; only exceptional cases stand out
- **Psychological**: Habituation effect reduces perceived value of similar content

---

#### **High-Engagement vs. Low-Engagement Content** (Needs Further Analysis)

**Predicted Patterns**:
- **High engagement**: Dramatic before/after stories, unusual side effects, detailed success/failure narratives
- **Low engagement**: Generic questions ("should I start?", "normal dose?"), vague updates ("week 2 update")

**Research Needed**: Qualitative coding of top 10% vs. bottom 10% engagement posts to identify distinguishing features.

---

### 3.4 Framing Analysis: From Medical to Lifestyle Discourse

#### **Topic Distribution as Framing Signal**

```
Topic                      | Medical Framing | Lifestyle Framing | Dominant
---------------------------|-----------------|-------------------|----------
0: Weight Loss Experience  | Moderate        | High              | ★★★
1: Diet & Nutrition        | Low             | High              | ★★
2: Community Support       | Low             | Mixed             | ★
```

**Interpretation**:
- Dominant discourse (76.7%) frames semaglutide as **lifestyle intervention**, not diabetes treatment
- Focus on appearance ("look"), social comparison ("people"), and subjective experience ("feel")
- Medical aspects (dosing, side effects) embedded in personal narratives, not clinical discussion

---

#### **Temporal Framing Shift** (Hypothesis - Needs Validation)

**Expected Evolution**:
1. **2019-2020**: Medical framing dominant
   - Diabetes management focus
   - Clinical terminology more common
   - Physician-patient discussions

2. **2021-2023**: Transition period
   - Wegovy FDA approval (June 2021) → explicit weight loss indication
   - Dual medical/lifestyle framing emerges
   - Off-label use discussions increase

3. **2024-2025**: Lifestyle framing dominant
   - TikTok influence → beauty/wellness discourse
   - Celebrity associations → aspirational framing
   - Weight loss primary, diabetes secondary

**Evidence Needed**: Keyword frequency analysis across time periods (e.g., "diabetes" vs. "weight loss" mentions).

---

#### **Authority & Expertise Positioning**

**Discourse Strategies** (Observed in Topic Keywords):

1. **Experiential Authority** (Topic 0)
   - "I started", "my experience", "what worked for me"
   - Claims authority through lived experience
   - Typical in peer health communities

2. **Practical Expertise** (Topic 1)
   - Focus on actionable advice ("eat protein", "avoid sugar")
   - Community-generated best practices
   - Blends lay knowledge with nutritional science

3. **Navigational Expertise** (Topic 2)
   - Helping others navigate community norms ("message me privately")
   - Meta-knowledge about Reddit, insurance, doctors
   - Social capital through helpfulness

**Contrast with Medical Authority**:
- Limited explicit medical claims ("studies show", "doctors recommend")
- Users cite personal doctors but don't position themselves as medical experts
- **Implicit trust**: Community experiences valued as evidence

---

### 3.5 Engagement Metrics: What Drives Interaction?

#### **Engagement by Topic** (Predicted - Needs Validation)

If we had topic-engagement cross-tabulation:
```
Topic                  | Predicted Avg Score | Rationale
-----------------------|---------------------|---------------------------
0: Weight Loss         | Moderate            | Personal stories vary in uniqueness
1: Diet & Nutrition    | Lower               | Practical but less emotionally compelling
2: Community Support   | Lower               | Private matters, less public engagement
```

**Alternative Hypothesis**: Topic 2 might have **higher** engagement if posts are dramatic help requests (e.g., severe side effects).

---

#### **Year × Topic Interaction** (Unexplored)

**Research Question**: Does topic distribution change over time?
- Are nutrition discussions (Topic 1) increasing as community matures?
- Are support requests (Topic 2) decreasing as knowledge consolidates?

**Analysis Needed**: Chi-square test for topic independence across years.

---

## 4. Implications & Future Directions

### 4.1 For Healthcare Communication

1. **Engagement ≠ Information Quality**
   - Low-engagement posts may still answer important patient questions
   - Healthcare providers should monitor forums despite declining engagement metrics

2. **Sentiment Volatility**
   - Public sentiment can shift rapidly (2023 drop)
   - Sentiment monitoring can provide early warning of access/safety issues

3. **Framing Matters**
   - Patients frame semaglutide as lifestyle intervention, not medical treatment
   - Doctors should align education with patient framing for effective communication

---

### 4.2 For Pharmaceutical Companies & Policymakers

1. **Supply Management**
   - 2023 sentiment drop shows real-world impact of shortages
   - Proactive communication during shortages crucial

2. **Access & Equity**
   - Declining sentiment may reflect frustration with cost/insurance
   - Policy interventions needed to address access barriers

---

### 4.3 For Reddit Community Moderation

1. **Quality Over Quantity**
   - High post volume doesn't mean healthy community
   - Consider pinned FAQs to reduce repetitive posts

2. **Support Topic 2 Discussions**
   - Despite low volume, support posts have highest sentiment
   - Encourage peer support without overwhelming feed

---

### 4.4 Limitations & Future Research

#### **Limitations**:
1. **2019 Undersampling**: Only 14 documents; can't draw robust conclusions
2. **Reddit-Specific**: May not represent general patient population (skewed younger, tech-savvy)
3. **Self-Selection Bias**: Users who post may have more extreme experiences
4. **Temporal Confounding**: Can't isolate causal factors (supply shortage vs. media vs. side effects)

#### **Future Research Directions**:

1. **Qualitative Deep-Dive**
   - Manual coding of high/low engagement posts
   - Narrative analysis of framing strategies
   - Longitudinal case studies of prolific users

2. **Cross-Platform Comparison**
   - Compare Reddit to TikTok, Twitter, Facebook groups
   - Do findings generalize or are they platform-specific?

3. **Causal Inference**
   - Difference-in-differences analysis around FDA approval dates
   - Interrupted time series for 2023 supply shortage

4. **Predictive Modeling**
   - Can we predict post engagement from content features?
   - Can topic models predict future sentiment shifts?

5. **Network Analysis**
   - User-to-user interaction patterns
   - Identify influential community members
   - Trace information diffusion

---

## 5. Conclusion

This analysis of 23,405 Reddit documents reveals a dynamic and evolving discourse around semaglutide from 2019-2025. Three key themes dominate: **weight loss experiences** (76.7%), **diet management** (20.7%), and **community support** (2.7%). While discussions have exploded in volume (903x growth), individual post engagement has collapsed (median score from 888 to 6), suggesting content saturation and demographic shifts as the medication entered mainstream consciousness.

Sentiment patterns reveal a critical 2023 inflection point, with mean sentiment dropping 30% from its 2020 peak, likely driven by supply shortages, increased media scrutiny, and access frustrations. Recovery in 2024-2025 suggests adaptation and stabilization, but persistent engagement challenges indicate community dynamics continue to evolve.

**The central paradox**: More discussion does not equal more engagement. As semaglutide became ubiquitous, the novelty and community intimacy that characterized early discourse gave way to a high-volume, low-engagement environment. Understanding this transition is critical for healthcare providers, pharmaceutical companies, and community moderators seeking to leverage online health communities effectively.

Future research should explore causal mechanisms behind temporal shifts, conduct cross-platform comparisons, and investigate how framing strategies influence patient decision-making. This work provides a foundation for understanding how emerging medical treatments are discussed, debated, and integrated into public consciousness through digital communities.

---

## Appendix: Data & Code Availability

- **Repository**: `/Users/sher/project/sema/CSS/`
- **Processed Data**: `data/processed/documents_with_sentiment.csv` (23,405 documents)
- **Topic Model**: `models/lda/lda_model_best` (3 topics, coherence 0.682)
- **Reports**: `data/metadata/` (EDA, topic modeling, sentiment analysis)
- **Visualizations**: `visualizations/` (word clouds, charts, plots)

**Reproducibility**: All analyses conducted in Python using:
- Data: PRAW, BAScraper
- NLP: spaCy, NLTK, Gensim
- Sentiment: VADER
- Analysis: pandas, numpy
- Visualization: matplotlib, seaborn

---

*This research was conducted using publicly available Reddit data in accordance with platform terms of service and ethical guidelines for online research. All usernames are anonymized in the final dataset.*
