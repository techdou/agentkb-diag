# Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach

Zhuowan Li<sup>1</sup> Cheng Li<sup>1</sup> Mingyang Zhang<sup>1</sup>

Qiaozhu Mei<sup>2</sup>\* Michael Bendersky<sup>1</sup>

<sup>1</sup> Google DeepMind <sup>2</sup> University of Michigan

<sup>1</sup> {zhuowan,chgli,mingyang,bemike}@google.com <sup>2</sup> qmei@umich.edu

## Abstract

Retrieval Augmented Generation (RAG) has been a powerful tool for Large Language Models (LLMs) to efficiently process overly lengthy contexts. However, recent LLMs like Gemini-1.5 and GPT-4 show exceptional capabilities to understand long contexts directly. We conduct a comprehensive comparison between RAG and long-context (LC) LLMs, aiming to leverage the strengths of both. We benchmark RAG and LC across various public datasets using three latest LLMs. Results reveal that when resourced sufficiently, LC consistently outperforms RAG in terms of average performance. However, RAG’s significantly lower cost remains a distinct advantage. Based on this observation, we propose SELF-ROUTE, a simple yet effective method that routes queries to RAG or LC based on model self-reflection. SELF-ROUTE significantly reduces the computation cost while maintaining a comparable performance to LC. Our findings provide a guideline for long-context applications of LLMs using RAG and LC.

## 1 Introduction

Retrieval augmented generation (RAG) has been shown to be a both effective and efficient approach for large language models (LLMs) to leverage external knowledge. RAG retrieves relevant information based on the query and then prompts an LLM to generate a response in the context of the retrieved information. This approach significantly expands LLM’s access to vast amounts of information at a minimal cost.

However, recent LLMs like Gemini and GPT-4 have demonstrated exceptional capabilities in understanding long contexts directly. For example, Gemini 1.5 can process up to 1 million tokens (Reid et al., 2024). This prompts the need for a systematic comparison between long-context (LC) LLMs and RAG: on one hand, RAG conceptually acts as a prior, regularizing the attention of LLMs onto retrieved segments, thus avoiding the distraction of the irrelevant information and saving unnecessary attention computations; on the other hand, largescale pretraining may enable LLMs to develop even stronger long-context capabilities. Therefore, we are motivated to compare RAG and LC, evaluating both their performance and efficiency.

![](images/b8bba35eab4fba8b0a89c9ba8809d205a515d1901e216c9f0b1cba9bb21d46e7.jpg)  
Figure 1: While long-context LLMs (LC) surpass RAG in long-context understanding, RAG is significantly more cost-efficient. Our approach, SELF-ROUTE, combining RAG and LC, achieves comparable performance to LC at a much lower cost.

In this work, we systematically benchmark RAG and LC on various public datasets, gaining a comprehensive understanding of their pros and cons, and ultimately combining them to get the best of both worlds. Different from findings in previous work (Xu et al., 2023), we find that LC consistently outperform RAG in almost all settings (when resourced sufficiently). This demonstrates the superior progress of recent LLMs in long-context understanding.

Despite the suboptimal performance, RAG remains relevant due to its significantly lower computational cost. In contrast to LC, RAG significantly decreases the input length to LLMs, leading to reduced costs, as LLM API pricing is typically based on the number of input tokens. (Google, 2024; OpenAI, 2024b)<sup>1</sup>. Moreover, our analysis reveals that the predictions from LC and RAG are identical for over 60% of queries. For these queries, RAG can reduce cost without sacrificing performance.

Based on this observation, we propose SELF-ROUTE, a simple yet effective method that routes various queries to RAG or LC based on model selfreflection. With SELF-ROUTE, we significantly reduce the cost while achieving overall performance comparable to LC. For example, the cost is reduced by 65% for Gemini-1.5-Pro and 39% for GPT-4O.

Fig. 1 shows the comparisons of LC, RAG and SELF-ROUTE using three recent LLMs: GPT-4O, GPT-3.5-Turbo and Gemini-1.5-Pro. In addition to quantitative evaluation, we provide a comprehensive analysis comparing RAG and LC, including common failure patterns of RAG, the trade-offs between cost and performance, and the results on additional synthetic datasets. Our analysis serves as a starting point, inspiring future improvements of RAG, and as a empirical guide for building longcontext applications using RAG and LC.

## 2 Related Work

Long-context LLMs. There has long been efforts for enabling LLMs to handle long contexts (Guo et al., 2022; Beltagy et al., 2020; Chen et al., 2023b). While recent LLMs like Gemini-1.5 (Reid et al., 2024), GPT-4 (Achiam et al., 2023), Claude-3 (Anthropic, 2024) achieve significantly larger context window size, long-context prompting is still expensive due to the quadratic computation cost of transformers regarding to the input token numbers. Recent work proposes methods to reduce cost by prompt compression (Jiang et al., 2023), model distillation (Hsieh et al., 2023), or LLM cascading (Chen et al., 2023a).

Retrieval-augmented generation. Augmenting LLMs with relevant information retrieved from various sources (Lewis et al., 2020) has been successful in complementing LLMs with external knowledge. RAG achieves good performance on tasks like language modeling (Khandelwal et al., 2019; Shi et al., 2023) and QA (Guu et al., 2020; Izacard and Grave, 2020), with a significantly lower computation cost (Borgeaud et al., 2022). Related to but different from our work, recently works augment

RAG with correction (Yan et al., 2024), critique (Asai et al., 2023), verification (Li et al., 2023), or adaptive search (Wang et al., 2023; Cheng et al., 2024; Jeong et al., 2024) to improve retrieval quality on knowledge-intensive tasks.

Long-context evaluation. Evaluating long-context models is challenging due to the difficulty in collecting and analyzing long texts. Recent researchers propose both synthetic tests like needlein-a-haystack (Greg Kamradt, 2023), Ruler (Hsieh et al., 2024), or Counting Stars (Song et al., 2024), and real datasets including LongBench (Bai et al., 2023), ∞Bench (Zhang et al., 2024), L-Eval (An et al., 2023), and others (Shaham et al., 2022; Yuan et al., 2024; Maharana et al., 2024). Evaluating on these datasets, recent works study the performance degradation over various context lengths (Levy et al., 2024; Hsieh et al., 2024), the lostin-the-middle phenomenon (Liu et al., 2024), and explore solutions (Kuratov et al., 2024). Related to our work, Xu et al. (2023) compare RAG and long-context prompting and find that long-context models still lags behind RAG. This is different from our findings, possibly due to consideration of stronger LLMs and longer contexts in our work.

## 3 Benchmarking RAG versus LC

## 3.1 Datasets and metrics

We evaluate on a subset of datasets from Long-Bench (Bai et al., 2023) and ∞Bench (Zhang et al., 2024), which are recent benchmarks containing a collection of new and existing datasets for LLM evaluation, covering both synthetic and real texts in multiple languages. LongBench contains a collection of 21 datasets, with an average context length of 7k words. ∞Bench consists of even longer contexts with an average length of 100k tokens.

Among the datasets, we mainly focus on tasks that are (a) in English, (b) real, and (c) query-based (e.g. summarization tasks do not contain queries for retrieving relevant information). This results in 7 datasets from LongBench including NarrativeQA (Kociskˇ y et al.\` , 2018), Qasper (Dasigi et al., 2021), MultiFieldQA (Bai et al., 2023), HotpotQA (Yang et al., 2018), 2WikiMultihopQA (Ho et al., 2020), MuSiQue (Trivedi et al., 2022), QMSum (Zhong et al., 2021); and 2 datasets from ∞Bench including En.QA and EN.MC. Please refer to Appendix A for more details. Additionally, in Sec. 5.4, we will provide an ablation a synthetic datasets PassKey from ∞Bench.

For evaluation metrics, we report F1 scores for the open-ended QA tasks, accuracy for the multichoice QA tasks, and ROUGE score for the summarization tasks.

## 3.2 Models and Retrievers

Three latest LLMs are evaluated, including Gemini-1.5-Pro (Reid et al., 2024), GPT-4O (OpenAI, 2024a), and GPT-3.5-Turbo (OpenAI, 2023) <sup>2</sup>. Gemini-1.5-Pro is a recent long-context LLM from Google, supporting up to 1 million tokens. GPT-4O, the newest lightweight yet strong LLM from OpenAI, supports 128k tokens. GPT-3.5-Turbo supports 16k tokens.

Two retrievers are used in our study: Contriever (Izacard et al., 2021), which is a contrastively trained dense retriever outperforming BM25 on BEIR datasets, and Dragon (Lin et al., 2023), which is a recent generalizable dense retriever achieving high performance in both supervised and zero-shot settings without complex late interaction. Following (Xu et al., 2023), we divide long contexts into chunks of 300 words, and select the top k chunks (default k = 5) based on the cosine similarity of the query embedding and the chunk embeddings. The chunks are ordered by the similarity scores, with the chunk index prepended at the beginning.

Since black-box LLMs are pretrained on unknown datasets, the leakage of evaluation datasets may occur. Especially, some of the evaluation datasets are based on Wikipedia, which has likely been seen by LLMs during during. In some cases, we find that model may predict the correct answer using exactly the same words as the groundtruth (e.g. “meticulously”), even when they do not appear in the provided context. In our experiment, we try mitigating this issue by prompting the model to answer “based only on the provided passage” for both RAG and LC. It remains an open question how to address the data leakage issue in LLM evaluation.

## 3.3 Benchmarking results

We benchmark the performance of LC and RAG across the nine datasets, using three recent LLMs: Gemini-1.5-Pro, GPT-4O and GPT-3.5-Turbo. Tab. 1 presents the results using the Contriever retriever, where rows \*-1 and rows \*-2 present the benchmarking results for LC and RAG respectively. Results using the Dragon retriever will be discussed

in Sec. 5.3 and Tab. 2.

As shown in Tab. 1, LC consistently outperforms RAG for all the three models, with a significant margin. On average, LC surpasses RAG by 7.6% for Gemini-1.5-Pro, 13.1% for GPT-4O, and 3.6% for GPT-3.5-Turbo. Noticeably, the performance gap is more significant for the more recent models (GPT-4O and Gemini-1.5-Pro) compared to GPT-3.5-Turbo, highlighting the exceptional longcontext understanding capacity of the latest LLMs.

However, there is an exception observed on the two longer datasets from ∞Bench (i.e., En.QA and En.MC), where RAG achieves higher performance than LC for GPT-3.5-Turbo. This result deviates from the overall trend, likely due to the significantly longer context in these datasets (147k words on average) compared with the limited context window (16k) of GPT-3.5-Turbo. This finding highlights the effectiveness of RAG when the input text considerably exceeds the model’s context window size, emphasizing a specific use case of RAG.

## 4 Self-Route

## 4.1 Motivation

As demonstrated in Sec. 3, RAG lags behind longcontext LLMs in terms of performance. However, despite this performance gap, we surprisingly find a high degree of overlap in their predictions, as illustrated in Fig. 2.

![](images/fb27c49af1ba0724a5381356a0225785ae3c3d74a070601edb8c08070d197335.jpg)  
Figure 2: Distribution of the difference of prediction scores between RAG and LC (computed w.r.t. groundtruth labels). RAG and LC predictions are highly identical, for both correct and incorrect ones.

Fig. 2 displays the distribution of the differences between RAG prediction scores $S _ { R A G }$ and LC prediction scores $S _ { L C }$ , specifically $S _ { R A G } - S _ { L C }$ (the scores are multiplied by 100 to be scaled to 1-100). These scores $S$ represent the evaluation of model predictions against the groundtruth. Notably, for most queries, RAG scores and LC scores are highly similar. In fact, for 63% queries, the model predictions are exactly identical; and for 70% queries, the score difference is less than 10 (absolute value). Interestingly, the identical predictions are not necessarily correct, as shown by the varying colors representing the average score, i.e., $( S _ { R A G } + S _ { L C } ) / 2$ This observation suggests that RAG and LC tend to make not only the same correct predictions but also similar errors.

<table><tr><td colspan="3"></td><td>Avg</td><td>Narr</td><td>Qasp</td><td>Mult</td><td>Hotp</td><td>2Wiki</td><td>Musi</td><td>Sum</td><td>En.QA</td><td>En.MC</td></tr><tr><td rowspan="5">Gemini-1.5-Pro</td><td>1-1</td><td>LC</td><td>49.70</td><td>32.76</td><td>47.83</td><td>52.33</td><td>61.85</td><td>62.96</td><td>40.22</td><td>20.73</td><td>43.08</td><td>85.57</td></tr><tr><td>1-2</td><td>RAG</td><td>37.33</td><td>22.54</td><td>44.68</td><td>49.53</td><td>48.36</td><td>54.24</td><td>26.56</td><td>19.51</td><td>19.46</td><td>51.09</td></tr><tr><td>1-3</td><td>SELF-ROUTE</td><td>46.41</td><td>28.32</td><td>45.23</td><td>51.47</td><td>55.18</td><td>62.68</td><td>40.66</td><td>19.77</td><td>37.51</td><td>76.86</td></tr><tr><td>1-4</td><td>answerable %</td><td>76.78</td><td>73.00</td><td>85.00</td><td>96.67</td><td>84.50</td><td>81.00</td><td>58.50</td><td>93.50</td><td>56.41</td><td>62.45</td></tr><tr><td>1-5</td><td>token %</td><td>38.39</td><td>23.07</td><td>49.93</td><td>36.88</td><td>32.97</td><td>53.49</td><td>56.14</td><td>17.96</td><td>42.25</td><td>32.84</td></tr><tr><td rowspan="5">GPT-4O</td><td>2-1</td><td>LC</td><td>48.67</td><td>32.78</td><td>44.54</td><td>55.28</td><td>62.42</td><td>70.69</td><td>41.65</td><td>21.92</td><td>32.36</td><td>76.42</td></tr><tr><td>2-2</td><td>RAG</td><td>32.60</td><td>18.05</td><td>46.02</td><td>50.74</td><td>36.86</td><td>50.21</td><td>16.09</td><td>19.97</td><td>14.43</td><td>41.05</td></tr><tr><td>2-3</td><td>SELF-ROUTE</td><td>48.89</td><td>31.36</td><td>47.99</td><td>53.17</td><td>62.14</td><td>70.14</td><td>41.69</td><td>21.31</td><td>34.95</td><td>77.29</td></tr><tr><td>2-4</td><td>answerable %</td><td>57.36</td><td>44.00</td><td>67.50</td><td>94.00</td><td>52.50</td><td>62.00</td><td>30.00</td><td>92.00</td><td>27.07</td><td>47.16</td></tr><tr><td>2-5</td><td>token %</td><td>61.40</td><td>66.40</td><td>72.25</td><td>39.65</td><td>65.79</td><td>77.05</td><td>85.00</td><td>20.26</td><td>73.01</td><td>53.21</td></tr><tr><td rowspan="5">GPT-3.5-Turbo</td><td>3-1</td><td>LC</td><td>32.07</td><td>23.34</td><td>42.96</td><td>49.19</td><td>45.33</td><td>41.04</td><td>17.92</td><td>19.61</td><td>14.73</td><td>34.50</td></tr><tr><td>3-2</td><td>RAG</td><td>30.33</td><td>18.22</td><td>38.15</td><td>49.21</td><td>37.84</td><td>35.16</td><td>16.41</td><td>18.94</td><td>15.39</td><td>43.67</td></tr><tr><td>3-3</td><td>SELF-ROUTE</td><td>35.32</td><td>24.06</td><td>38.65</td><td>52.07</td><td>47.28</td><td>44.62</td><td>34.44</td><td>19.88</td><td>22.03</td><td>44.54</td></tr><tr><td>3-4</td><td>answerable %</td><td>74.10</td><td>71.50</td><td>80.00</td><td>91.33</td><td>68.50</td><td>69.00</td><td>47.00</td><td>93.50</td><td>50.43</td><td>95.63</td></tr><tr><td>3-5</td><td>token %</td><td>38.85</td><td>20.56</td><td>55.08</td><td>35.29</td><td>48.70</td><td>65.91</td><td>65.08</td><td>16.40</td><td>38.17</td><td>4.50</td></tr></table>

Table 1: Results of Gemini-1.5-Pro, GPT-3.5-Turbo, and GPT-4O using the Contriever retriever. LC consistently outperforms RAG, while SELF-ROUTE achieves performance comparable to LC using much less tokens.

This finding motivates us to leverage RAG for the majority of queries, reserving computationally more expensive LC for a small subset of queries where it truly excels. By doing so, RAG can significantly reduce computational costs without sacrificing overall performance.

## 4.2 Self-Route

Based on the above motivation, we propose SELF-ROUTE, a simple yet effective method combining RAG and LC to reduce cost while maintaining a performance comparable to LC. SELF-ROUTE utilizes LLM itself to route queries based on selfreflection, under the assumption that LLMs are well-calibrated in predicting whether a query is answerable given provided context.

Concretely, our method consists of two steps: a RAG-and-Route step and a long-context prediction step. In the first step, we provide the query and the retrieved chunks to the LLM, and prompt it to predict whether the query is answerable and, if so, generate the answer. This is similar to standard RAG, with one key difference: the LLM is given the option to decline answering with the prompt “Write unanswerable if the query can not be answered based on the provided text”. For the queries deemed answerable, we accept the RAG prediction as the final answer. For the queries deemed unanswerable, we proceed to the second step, providing the full context to the long-context LLMs to obtain the final prediction (i.e., LC).

As our results will demonstrate, most queries can be solved by the first RAG-and-Route step (e.g., 82% for Gemini-1.5-Pro), with only a small portion requiring the following long-context prediction step. Since the RAG-and-Route step only needs the retrieved chunks (e.g., 1.5k tokens) as input, which is significantly shorter than the full contexts (e.g., 10k - 100k tokens), the overall computation cost is substantially reduced. Detailed token count analysis will be provided in the results.

## 4.3 Results

Rows \*-3 to \*-5 in Tab. 1 present the results of our method, utilizing the three LLMs. Rows \*-3 report the performance. Rows \*-4 show the percentage of answerable queries, as predicted in the RAGand-Route step. Rows \*-5 display the percentage of tokens used by our method, compared to that of LC. In terms of performance (rows \*-3), SELF-ROUTE significantly outperforms RAG, achieving results comparable to LC. Across all three models, SELF-ROUTE surpasses RAG (rows \*-2) by over 5%. Compared to LC (rows \*-1), there is a slight performance drop for GPT-4O (-0.2%) and Gemini-1.5-Pro (-2.2%), but an improvement for GPT-3.5- Turbo (+1.7%).

All three LLMs consistently route more than half of queries towards RAG, as shown in rows \*-4. For Gemini-1.5-Pro, the answerable percentage even reaches 81.74% (row 1-4). This indicates that RAG may answer most queries without the need for LC, confirming our initial motivation.

Due to the high answerable rate, the number of tokens required is significantly reduced (rows \*- 5). For example, GPT-4O uses only 61% tokens while achieving comparable performance (46.83) with LC (47.04), Gemini-1.5-Pro uses 38.6% of the tokens. Since the computation cost of the transformer-based LLMs is quadratic to token count, and most LLM APIs charge based on token count (OpenAI, 2024b; Google, 2024), this lower token count translates to substantial cost savings.

On longer datasets, the advantage of our method is more pronounced for OpenAI models, but less significant for Gemini. For instance, for GPT-4O, SELF-ROUTE outperforms LC by 2.3% and 7.4% respectively on EN.QA and EN.MC, which contain longer contexts. For GPT-3.5-Turbo, the advantage margins are even larger. However, for Gemini-1.5-Pro, the performance is lower than LC. These different behaviors are possibly due to the difference in LLM alignments, i.e., OpenAI models are more likely to reject answering using RAG, leading to a lower answerable percentage but higher accuracy, which results in a different performance-cost trade-off compared with Gemini-1.5-Pro.

## 5 Analysis

## 5.1 Ablations of k

Both RAG and SELF-ROUTE relies on the top-k retrieved text chunks. The larger k is, the longer context are fed into LLMs for RAG prediction as well as routing, resulting in different costs versus performances. To study the influence of k, in Fig. 3, we plot the performance and cost (i.e. input token percentage) curves when different ks are used.

In terms of performance, for both RAG and SELF-ROUTE, a larger k leads to better performance. While k increases, more and more chunks are fed into the LLMs, thus the performance gradually improves to approach LC. As can be seen in from the curves, the advantage of SELF-ROUTE is the most significant for smaller k. For example, when k = 1, RAG gets from 20.24% while SELF-ROUTE gets 37.9%, while when k is larger than 50, all three methods get similar performance.

However, the trend of cost is not monotonous for SELF-ROUTE. As seen, the cost reaches its minimum at $k = 5 .$ This is because when k increases, the cost of RAG (and routing) increases, but more queries are routed to RAG from LC, thus the overall cost may decrease. The sweet point of k might be different for each dataset, e.g. on average, k = 5 has the lowest cost as shown in the curves, but on some datasets, especially ones that contain extractive questions which does not need multi-hop reasoning (like NarrativeQA and QMSum), k = 1 leads to the lowest cost. This indicates that the optimal k depends on the nature of the task, as well as the performance requirement. We encourage future researchers to look for different ks when applying our method to various applications.

![](images/aff9b1a7c68c2b69a55bc5a62036013a6ba5f9163556f8114267aab800d2f8a0.jpg)  
Figure 3: Trade-off curves between (a) model performance and (b) token percentage as a function of k.

## 5.2 Why does RAG fail?

To gain a better understanding of why RAG lags behind LC, we analyze the failure reasons for the examples that cannot be answered by RAG. We first manually check some examples for which our RAG-and-Route step predicts “unanswerable” and summarize four typical failure reasons, then prompt LLM to classify all the examples.

The four reasons include: (A) The query requires multi-step reasoning so the results of previous steps are needed to retrieve information for later steps, e.g. “What nationality is the performer of song XXX”. (B) The query is general, e.g. “What does the group think about XXX”, which is challenging for the retriever to formulate a good query. (C) The query is long and complex, which is challenging for the retriever to understand. However, answering this kind of questions is arguably, an advantage of LLMs. (D) The query is implicit, demanding a thorough understanding of the entire context. For instance, in a lengthy conversational narrative about a space voyage, a question like “What caused the shadow behind the spaceship?” requires readers to connect the dots and deduce the answer, as there is no explicit mention of the shadow when the cause is revealed.

<table><tr><td colspan="3"></td><td>Avg</td><td>Narr</td><td>Qasp</td><td>Mult</td><td>Hotp</td><td>2Wiki</td><td>Musi</td><td>Sum</td><td>En.QA</td><td>En.MC</td></tr><tr><td rowspan="5">Dragon</td><td>1</td><td>LC</td><td>49.70</td><td>32.76</td><td>47.83</td><td>52.33</td><td>61.85</td><td>62.96</td><td>40.22</td><td>20.73</td><td>43.08</td><td>85.57</td></tr><tr><td>2</td><td>RAG</td><td>38.09</td><td>21.91</td><td>44.33</td><td>53.08</td><td>51.61</td><td>50.05</td><td>30.47</td><td>19.93</td><td>21.25</td><td>50.22</td></tr><tr><td>3</td><td>combine</td><td>46.81</td><td>28.50</td><td>43.82</td><td>54.62</td><td>56.58</td><td>60.62</td><td>40.66</td><td>20.07</td><td>37.79</td><td>78.60</td></tr><tr><td>4</td><td>RAG ratio</td><td>77.88</td><td>74.00</td><td>84.00</td><td>97.33</td><td>86.00</td><td>77.00</td><td>66.00</td><td>95.50</td><td>61.25</td><td>59.83</td></tr><tr><td>5</td><td>Token ratio</td><td>37.87</td><td>19.31</td><td>54.15</td><td>34.78</td><td>32.64</td><td>55.65</td><td>48.16</td><td>16.64</td><td>38.71</td><td>40.83</td></tr></table>

Table 2: Results for Gemini-1.5-Pro using Dragon retriever.

![](images/7107a0de0b29a385e6ee891593d7e3400c1f3d284c89bb5cf7334fd3cd673a5c.jpg)  
Figure 4: Distribution of typical RAG failure reasons.

Using these reasons, we prompt Gemini-1.5-Pro with few-shot in-context examples that we manually annotated, to classify all the unanswerable examples into these four categories, plus an “other" option. Fig. 4 shows the distribution of failure reasons on the seven datasets in LongBench. Each dataset may contain different number of RAG failure cases, resulting in various bar heights. The distribution patterns are consistent with the nature of the datasets. For example, the three Wikipediabased multi-hop reasoning datasets (HotpotQA, 2WikiMQA, MuSiQue) are challenging for RAG because of multi-step retrieval as shown in blue. For NarrativeQA, which are long stories containing a lot of dialogues, most failure cases are due to implicit queries that requires understanding the whole context (shown in green). For QMSum, which is a summarization dataset contains open-ended questions, failures are mostly due to general queries (shown in red). We manually checked the examples classified as “others” and find that most of them are actually multi-step questions, often with ambiguities, which poses challenges for answering.

We hope this failure analysis inspires future improvements of RAG. For example, engaging chainof-thought (Wei et al., 2022) into RAG may help address the multi-step questions, and revisiting query understanding techniques like query expansion (Lv and Zhai, 2009; Zhai and Lafferty, 2001) may help with the general queries and complex queries. We are also glad to see recent efforts towards the direction (Chan et al., 2024; Ma et al., 2023).

## 5.3 Different retrievers

The results using a retriever, Dragon, is shown in Tab. 2 based on Gemini-1.5-Pro. As can be seen, the results are consistent with Contriever, for all of LC, RAG, and SELF-ROUTE, showing that our findings are generalizable across retrievers.

## 5.4 Results on synthetic data

In this study, we mainly focus on real datasets, with a consideration that results on synthetic data, which are artificially created by researchers, may subject to dataset artifacts. We notice some methods that researchers adopted to create synthetic long context datasets may unconsciously, but largely, influence the performance comparison between RAG and LC. For example, here we describe the results on the “PassKey” dataset in ∞Bench and its variations.

This “PassKey” dataset presents a needle-in-ahaystack test, where a sentence with a passkey (e.g. “the passkey is 123456”) is hidden within chunks of irrelevant text, and the model is asked to answer the question “What is the passkey”. The task requires strong retrieval capability. On this dataset, RAG achieves 80.34% accuracy, outperforming LC, which gets 65.25% using Gemini-1.5-Pro. However, if the query is slightly modified as “What is the special token hidden inside the texts”, RAG accuracy sharply drops to only 4.58%, while LC keeps roughly the same (69.32%). Another example: if the chunks contain two passkeys and the query is “Which passkey is larger? First or second?”, then RAG (47.63%) under-performs LC (64.24%) as well.

<table><tr><td></td><td>RAG</td><td>LC</td></tr><tr><td>Original</td><td>80.34</td><td>65.25</td></tr><tr><td>Variant-1: “special token”</td><td>4.58</td><td>69.32</td></tr><tr><td>Variant-2: “which is larger”</td><td>47.63</td><td>64.24</td></tr></table>

Table 3: Synthetic dataset may unconsciously contain artifacts that influence the comparison results.

Tab. 3 summarizes the results, which demonstrates that the evaluation highly subjects to artifacts in dataset construction, showing limitation of synthetic testing.

## 5.5 Exclusion of LLM’s internal knowledge

Ideally, the comparison in this paper should exclude the model’s internal knowledge (i.e., parametric knowledge) so that the model’s performance are solely based on its capability to understand long contexts. In our study, this internal knowledge is excluded by utilizing the prompt “based only on the provided passage”, which we empirically find is a simple yet effective method. Here we discuss the effectiveness of this method, as well as alternative methods to exclude external knowledge.

First, we validate the effectiveness of the simple prompt “based only on the provided passage”. Tab. 4 compares the performance (long-context) of Gemini-1.5-Pro with and without this prompt. As shown, using this prompt consistently limits the model’s performance (average performance drops from 50.57 to 45.53), which indicates that using this simple instruction can already effectively limit the usage of the model’s parametric knowledge.

<table><tr><td></td><td>without&quot;based only on ...&quot;</td><td>with&quot;based only on ...&quot;</td></tr><tr><td>NarrativeQA</td><td>36.35</td><td>32.76</td></tr><tr><td>Qasper</td><td>50.69</td><td>47.83</td></tr><tr><td>MultiFieldQA</td><td>56.07</td><td>52.33</td></tr><tr><td>HotpotQA</td><td>66.47</td><td>61.85</td></tr><tr><td>2WikiMQA</td><td>68.97</td><td>62.96</td></tr><tr><td>Musique</td><td>54.56</td><td>40.22</td></tr><tr><td>QMSum</td><td>20.87</td><td>20.73</td></tr><tr><td>En.QA</td><td>49.20</td><td>43.08</td></tr><tr><td>En.MC</td><td>90.83</td><td>85.57</td></tr><tr><td>Avg</td><td>50.57</td><td>45.53</td></tr></table>

Table 4: Comparison of the long-context performance of Gemini-1.5-Pro, using the prompt with and without “based only on the provided passage”.

Second, as an alternative method to exclude internal knowledge, we remove the questions where the model can correctly answer without any contexts (i.e., commonsense questions), and report the model’s performance only on the noncommonsense questions. Tab. 5 shows the performance of Gemini-1.5-Pro and GPT-3.5-Turbo on all the questions from the MuSiQue dataset, as well as their performance on the non-commonsense subset<sup>3</sup>. As shown, after excluding the commonsense questions, the trend remains the same.

<table><tr><td rowspan="2"></td><td colspan="2">all questions</td><td colspan="2">w/o commonsense</td></tr><tr><td>Gemini</td><td>GPT-3.5</td><td>Gemini</td><td>GPT-3.5</td></tr><tr><td># questions</td><td>200</td><td>200</td><td>133</td><td>150</td></tr><tr><td>LC</td><td>40.22</td><td>17.92</td><td>31.76</td><td>13.00</td></tr><tr><td>RAG</td><td>26.56</td><td>16.41</td><td>15.51</td><td>13.05</td></tr><tr><td>Self-Route</td><td>40.66</td><td>34.44</td><td>31.32</td><td>19.76</td></tr><tr><td>answerable %</td><td>58.50</td><td>47.00</td><td>52.63</td><td>45.33</td></tr><tr><td>token %</td><td>56.14</td><td>65.08</td><td>48.46</td><td>53.43</td></tr></table>

Table 5: Results on MuSiQue on all questions, and on the subset of non-commonsense questions (i.e., excluding questions that can be answered without contexts).

That said, a more thorough study to explore various methods for controlling the usage of model’s internal knowledge, and to study the source of internal knowledge (e.g. LLM"s world knowledge or dataset leakage), will be valuable future work, which we hope can be further investigated.

## 6 conclusion

This paper presents a comprehensive comparison of RAG and LC, highlighting the trade-offs between performance and computational cost. While LC demonstrate superior performance in long-context understanding, RAG remains a viable option due to its lower cost and advantages when the input considerably exceeds the model’s context window size. Our proposed method, which dynamically routes queries based on model self-reflection, effectively combines the strengths of both RAG and LC, achieving comparable performance to LC at a significantly reduced cost. We believe our findings contribute valuable insights for the practical application of long-context LLMs and pave the way for future research in optimizing RAG techniques.

## Acknowledgements

We would like to thank Weize Kong, Tao Chen, Jeffrey Dudek and Spurthi Amba Hombaiah for their helpful comments and suggestions, as well as the anonymous reviewers for the valuable discussions.

## References

Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo Almeida, Janko Altenschmidt, Sam Altman, Shyamal Anadkat, et al. 2023. Gpt-4 technical report. arXiv preprint arXiv:2303.08774.

Chenxin An, Shansan Gong, Ming Zhong, Mukai Li, Jun Zhang, Lingpeng Kong, and Xipeng Qiu. 2023. L-eval: Instituting standardized evaluation for long context language models. arXiv preprint arXiv:2307.11088.

Anthropic. 2024. Claude 3.5 sonnet. https://www. anthropic.com/news/claude-3-5-sonnet/.

Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, and Hannaneh Hajishirzi. 2023. Self-rag: Learning to retrieve, generate, and critique through self-reflection. arXiv preprint arXiv:2310.11511.

Yushi Bai, Xin Lv, Jiajie Zhang, Hongchang Lyu, Jiankai Tang, Zhidian Huang, Zhengxiao Du, Xiao Liu, Aohan Zeng, Lei Hou, et al. 2023. Longbench: A bilingual, multitask benchmark for long context understanding. arXiv preprint arXiv:2308.14508.

Iz Beltagy, Matthew E Peters, and Arman Cohan. 2020. Longformer: The long-document transformer. arXiv preprint arXiv:2004.05150.

Sebastian Borgeaud, Arthur Mensch, Jordan Hoffmann, Trevor Cai, Eliza Rutherford, Katie Millican, George Bm Van Den Driessche, Jean-Baptiste Lespiau, Bogdan Damoc, Aidan Clark, et al. 2022. Improving language models by retrieving from trillions of tokens. In International conference on machine learning, pages 2206–2240. PMLR.

Chi-Min Chan, Chunpu Xu, Ruibin Yuan, Hongyin Luo, Wei Xue, Yike Guo, and Jie Fu. 2024. Rq-rag: Learning to refine queries for retrieval augmented generation. arXiv preprint arXiv:2404.00610.

Lingjiao Chen, Matei Zaharia, and James Zou. 2023a. Frugalgpt: How to use large language models while reducing cost and improving performance. arXiv preprint arXiv:2305.05176.

Shouyuan Chen, Sherman Wong, Liangjian Chen, and Yuandong Tian. 2023b. Extending context window of large language models via positional interpolation. arXiv preprint arXiv:2306.15595.

Qinyuan Cheng, Xiaonan Li, Shimin Li, Qin Zhu, Zhangyue Yin, Yunfan Shao, Linyang Li, Tianxi ang Sun, Hang Yan, and Xipeng Qiu. 2024. Unified

active retrieval for retrieval augmented generation. arXiv preprint arXiv:2406.12534.

Pradeep Dasigi, Kyle Lo, Iz Beltagy, Arman Cohan, Noah A Smith, and Matt Gardner. 2021. A dataset of information-seeking questions and answers anchored in research papers. arXiv preprint arXiv:2105.03011.

Google. 2024. Gemini pricing. https://ai.google. dev/pricing.

Greg Kamradt. 2023. Needle in a haystack - pressure testing llms. https://github.com/gkamradt/ LLMTest\_NeedleInAHaystack.

Mandy Guo, Joshua Ainslie, David C Uthus, Santiago Ontanon, Jianmo Ni, Yun-Hsuan Sung, and Yinfei Yang. 2022. Longt5: Efficient text-to-text transformer for long sequences. In Findings of the Association for Computational Linguistics: NAACL 2022, pages 724–736.

Kelvin Guu, Kenton Lee, Zora Tung, Panupong Pasupat, and Mingwei Chang. 2020. Retrieval augmented language model pre-training. In International conference on machine learning, pages 3929–3938. PMLR.

Xanh Ho, Anh-Khoa Duong Nguyen, Saku Sugawara, and Akiko Aizawa. 2020. Constructing a multi-hop qa dataset for comprehensive evaluation of reasoning steps. arXiv preprint arXiv:2011.01060.

Cheng-Ping Hsieh, Simeng Sun, Samuel Kriman, Shantanu Acharya, Dima Rekesh, Fei Jia, and Boris Ginsburg. 2024. Ruler: What’s the real context size of your long-context language models? arXiv preprint arXiv:2404.06654.

Cheng-Yu Hsieh, Chun-Liang Li, Chih-Kuan Yeh, Hootan Nakhost, Yasuhisa Fujii, Alexander Ratner, Ranjay Krishna, Chen-Yu Lee, and Tomas Pfister. 2023. Distilling step-by-step! outperforming larger language models with less training data and smaller model sizes. arXiv preprint arXiv:2305.02301.

Gautier Izacard, Mathilde Caron, Lucas Hosseini, Sebastian Riedel, Piotr Bojanowski, Armand Joulin, and Edouard Grave. 2021. Unsupervised dense information retrieval with contrastive learning. arXiv preprint arXiv:2112.09118.

Gautier Izacard and Edouard Grave. 2020. Leveraging passage retrieval with generative models for open domain question answering. arXiv preprint arXiv:2007.01282.

Soyeong Jeong, Jinheon Baek, Sukmin Cho, Sung Ju Hwang, and Jong C Park. 2024. Adaptive-rag: Learning to adapt retrieval-augmented large language models through question complexity. In Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers), pages 7029–7043.

Huiqiang Jiang, Qianhui Wu, Xufang Luo, Dongsheng Li, Chin-Yew Lin, Yuqing Yang, and Lili Qiu. 2023. Longllmlingua: Accelerating and enhancing llms in long context scenarios via prompt compression. arXiv preprint arXiv:2310.06839.

Urvashi Khandelwal, Omer Levy, Dan Jurafsky, Luke Zettlemoyer, and Mike Lewis. 2019. Generalization through memorization: Nearest neighbor language models. arXiv preprint arXiv:1911.00172.

Tomáš Kociskˇ y, Jonathan Schwarz, Phil Blunsom, Chris\` Dyer, Karl Moritz Hermann, Gábor Melis, and Ed ward Grefenstette. 2018. The narrativeqa reading comprehension challenge. Transactions of the Association for Computational Linguistics, 6:317–328.

Yuri Kuratov, Aydar Bulatov, Petr Anokhin, Dmitry Sorokin, Artyom Sorokin, and Mikhail Burtsev. 2024. In search of needles in a 10m haystack: Recurrent memory finds what llms miss. arXiv preprint arXiv:2402.10790.

Mosh Levy, Alon Jacoby, and Yoav Goldberg. 2024. Same task, more tokens: the impact of input length on the reasoning performance of large language models. arXiv preprint arXiv:2402.14848.

Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih, Tim Rock täschel, et al. 2020. Retrieval-augmented generation for knowledge-intensive nlp tasks. Advances in Neural Information Processing Systems, 33:9459–9474.

Xiaonan Li, Changtai Zhu, Linyang Li, Zhangyue Yin, Tianxiang Sun, and Xipeng Qiu. 2023. Llatrieval: Llm-verified retrieval for verifiable generation. arXiv preprint arXiv:2311.07838.

Sheng-Chieh Lin, Akari Asai, Minghan Li, Barlas Oguz, Jimmy Lin, Yashar Mehdad, Wen-tau Yih, and Xilun Chen. 2023. How to train your dragon: Diverse augmentation towards generalizable dense retrieval. arXiv preprint arXiv:2302.07452.

Nelson F Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, and Percy Liang. 2024. Lost in the middle: How language mod els use long contexts. Transactions of the Association for Computational Linguistics, 12:157–173.

Yuanhua Lv and ChengXiang Zhai. 2009. Adaptive relevance feedback in information retrieval. In Proceedings of the 18th ACM conference on Information and knowledge management, pages 255–264.

Xinbei Ma, Yeyun Gong, Pengcheng He, Hai Zhao, and Nan Duan. 2023. Query rewriting for retrievalaugmented large language models. arXiv preprint arXiv:2305.14283.

Adyasha Maharana, Dong-Ho Lee, Sergey Tulyakov, Mohit Bansal, Francesco Barbieri, and Yuwei Fang. 2024. Evaluating very long-term conversational memory of llm agents. arXiv preprint arXiv:2402.17753.

OpenAI. 2023. Gpt-3.5-turbo. https://platform. openai.com/docs/models/gpt-3-5-turbo.

OpenAI. 2024a. Gpt-4o. https://openai.com/ index/hello-gpt-4o/.

OpenAI. 2024b. Openai-api pricing. https:// platform.openai.com/docs/overview.

Machel Reid, Nikolay Savinov, Denis Teplyashin, Dmitry Lepikhin, Timothy Lillicrap, Jean-baptiste Alayrac, Radu Soricut, Angeliki Lazaridou, Orhan Firat, Julian Schrittwieser, et al. 2024. Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context. arXiv preprint arXiv:2403.05530.

Uri Shaham, Elad Segal, Maor Ivgi, Avia Efrat, Ori Yoran, Adi Haviv, Ankit Gupta, Wenhan Xiong, Mor Geva, Jonathan Berant, et al. 2022. Scrolls: Standardized comparison over long language sequences. arXiv preprint arXiv:2201.03533.

Weijia Shi, Sewon Min, Michihiro Yasunaga, Minjoon Seo, Rich James, Mike Lewis, Luke Zettlemoyer, and Wen-tau Yih. 2023. Replug: Retrievalaugmented black-box language models. arXiv preprint arXiv:2301.12652.

Mingyang Song, Mao Zheng, and Xuan Luo. 2024. Counting-stars: A simple, efficient, and reasonable strategy for evaluating long-context large language models. arXiv preprint arXiv:2403.11802.

Harsh Trivedi, Niranjan Balasubramanian, Tushar Khot, and Ashish Sabharwal. 2022. Musique: Multihop questions via single-hop question composition. Transactions of the Association for Computational Linguistics, 10:539–554.

Yile Wang, Peng Li, Maosong Sun, and Yang Liu. 2023. Self-knowledge guided retrieval augmentation for large language models. In Findings of the Association for Computational Linguistics: EMNLP 2023, pages 10303–10315.

Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Fei Xia, Ed Chi, Quoc V Le, Denny Zhou, et al. 2022. Chain-of-thought prompting elicits reasoning in large language models. Advances in neural information processing systems, 35:24824–24837.

Peng Xu, Wei Ping, Xianchao Wu, Lawrence McAfee, Chen Zhu, Zihan Liu, Sandeep Subramanian, Evelina Bakhturina, Mohammad Shoeybi, and Bryan Catanzaro. 2023. Retrieval meets long context large language models. arXiv preprint arXiv:2310.03025.

Shi-Qi Yan, Jia-Chen Gu, Yun Zhu, and Zhen-Hua Ling. 2024. Corrective retrieval augmented generation. arXiv preprint arXiv:2401.15884.

Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Bengio, William W Cohen, Ruslan Salakhutdinov, and Christopher D Manning. 2018. Hotpotqa: A dataset for diverse, explainable multi-hop question answering. arXiv preprint arXiv:1809.09600.

Tao Yuan, Xuefei Ning, Dong Zhou, Zhijie Yang, Shiyao Li, Minghui Zhuang, Zheyue Tan, Zhuyu Yao, Dahua Lin, Boxun Li, et al. 2024. Lv-eval: A balanced long-context benchmark with 5 length levels up to 256k. arXiv preprint arXiv:2402.05136.

Chengxiang Zhai and John Lafferty. 2001. Model-based feedback in the language modeling approach to information retrieval. In Proceedings of the tenth inter national conference on Information and knowledge management, pages 403–410.

Xinrong Zhang, Yingfa Chen, Shengding Hu, Zihang Xu, Junhao Chen, Moo Khai Hao, Xu Han, Zhen Leng Thai, Shuo Wang, Zhiyuan Liu, et al. 2024. Infinity bench: Extending long context evaluation beyond 100k tokens. arXiv preprint arXiv:2402.13718.

Ming Zhong, Da Yin, Tao Yu, Ahmad Zaidi, Mutethia Mutuma, Rahul Jha, Ahmed Hassan Awadallah, Asli Celikyilmaz, Yang Liu, Xipeng Qiu, et al. 2021. Qmsum: A new benchmark for query-based multidomain meeting summarization. arXiv preprint arXiv:2104.05938.

## A Dataset details

We evaluate on 7 datasets from LongBench (Bai et al., 2023). NarrativeQA (Kociskˇ y et al.\` , 2018) is a question answering dataset, where the context is a long story like a novel or a movie script. Qasper (Dasigi et al., 2021) focuses on question answering over academic NLP papers and is annotated by NLP practitioners. MultiFieldQA, originally proposed in LongBench, contains human-annotated QA over documents and articles from multiple sources, including legal documents, government reports, encyclopedias, academic papers, etc. HotpotQA (Yang et al., 2018) contains two-hop questions written by native English speakers that requires reasoning over two related Wikipedia paragraphs in the long context. 2WikiMultihopQA (Ho et al., 2020) contains up to 5-hop questions that are synthesized through manually designed templates, ensuring that they cannot be solved through shortcuts. The questions in MuSiQue (Trivedi et al., 2022) are up to 4-hop, first constructed from single-hop question compositions, and then paraphrased by annotators for linguistic diversity. QMSum (Zhong et al., 2021) is a query-based summarization dataset over meeting scripts from multiple domains.

We evaluate on 2 datasets from ∞Bench (Zhang et al., 2024). En.QA contains human-annotated question-answer pairs for long novels, with key entity names manually replaced in order to avoid knowledge leakage due to model pretraining. EN.MC is annotated similarly to En.QA, but differs in that the model is presented with four challenging answer choices written by the annotators.

Tab. 6 shows the details of the datasets, including the number of queries in each evaluation dataset and the average context length (i.e. number of words).

<table><tr><td></td><td></td><td>Num. Query</td><td>Avg. Length</td></tr><tr><td rowspan="7">LongBench(Bai et al., 2023)</td><td>NarrativeQA</td><td>200</td><td>18,395</td></tr><tr><td>Qasper</td><td>200</td><td>3,599</td></tr><tr><td>MultiFieldQA</td><td>150</td><td>4,539</td></tr><tr><td>HotpotQA</td><td>200</td><td>9,133</td></tr><tr><td>2WikiMultihopQA</td><td>200</td><td>4,873</td></tr><tr><td>MuSiQue</td><td>200</td><td>11,196</td></tr><tr><td>QMSum</td><td>200</td><td>10,533</td></tr><tr><td rowspan="2">∞Bench(Zhang et al., 2024)</td><td>En.QA</td><td>351</td><td>150,374</td></tr><tr><td>En.MC</td><td>229</td><td>142,622</td></tr></table>

Table 6: Dataset statistics.

## B Ablations of k

Tab. 7 shows the performance and token ratio for different k, which corresponds to Fig. 3. The performance of LC, which serves as an upper bound, is 45.53. The token ratio is computed the token counts for RAG or SELF-ROUTE divided the number of tokens required by LC.

<table><tr><td rowspan="2">top-k</td><td colspan="2">performance</td><td colspan="2">token ratio</td></tr><tr><td>RAG</td><td>Self-Route</td><td>RAG</td><td>Self-Route</td></tr><tr><td>1</td><td>20.24</td><td>41.35</td><td>5.26</td><td>39.64</td></tr><tr><td>5</td><td>37.92</td><td>43.33</td><td>17.02</td><td>38.63</td></tr><tr><td>10</td><td>41.20</td><td>44.38</td><td>42.42</td><td>53.66</td></tr><tr><td>50</td><td>44.06</td><td>45.19</td><td>95.29</td><td>102.97</td></tr><tr><td>100</td><td>44.12</td><td>45.23</td><td>100.32</td><td>106.59</td></tr></table>

Table 7: Performance and token ratio for different k. This table corresponds to Fig. 3.

## C Prompts

Tab. 9 shows the prompts for each dataset in our study. The prompts are modified from the released prompts as in LongBench (Bai et al., 2023) and ∞Bench (Zhang et al., 2024). Tab. 8 shows the prompts used in the failure case study as in Sec. 5.2.

![](images/e849c211cde88e5461a8708f0afef904e93bc021886598f7bdf76ceac718cd3b.jpg)  
Table 8: Prompt for the failure case analysis.

<table><tr><td>NarrativeQA</td><td>You are given a story, which can be either a novel or a movie script, and a question. Answer the question as concisely as you can, using a single phrase if possible. Do not provide any explanation. If the question cannot be answered based on the information in the article, write “unanswerable”. Story: {context} Now, answer the question based on the story as concisely as you can, using a single phrase if possible. Do not provide any explanation. If the question cannot be answered based on the information in the article, write “unanswerable”. Question: {input} Answer:</td></tr><tr><td>Qasper</td><td>You are given a scientific article and a question. Answer the question as concisely as you can, using a single phrase or sentence if possible. If the question cannot be answered based on the information in the article, write “unanswerable”. If the question is a yes/no question, answer “yes”, “no”, or “unanswerable”. Do not provide any explanation. Article: {context} Answer the question based on the above article as concisely as you can, using a single phrase or sentence if possible. If the question cannot be answered based on the information in the article, write “unanswerable”. If the question is a yes/no question, answer “yes”, “no”, or “unanswerable”. Do not provide any explanation. Question: input Answer:</td></tr><tr><td>MultiFQA</td><td>Read the following text and answer briefly. {context} Now, answer the following question based on the above text, only give me the answer and do not output any other words. If the question cannot be answered based on the information in the article, write “unanswerable”. Question: {input} Answer:</td></tr><tr><td>HotpotQA</td><td>Answer the question based on the given passages. Only give me the answer and do not output any other words. If the question cannot be answered based on the information in the article, write “unanswerable”. The following are given passages. {context} Answer the question based on the given passages. Only give me the answer and do not output any other words. If the question cannot be answered based on the information in the article, write “unanswerable”. Question: {input} Answer:</td></tr><tr><td>2WikiMQA</td><td>Answer the question based on the given passages. Only give me the answer and do not output any other words. If the question cannot be answered based on the information in the article, write “unanswerable”. The following are given passages. {context} Answer the question based on the given passages. Only give me the answer and do not output any other words. If the question cannot be answered based on the information in the article, write “unanswerable”. Question: {input}Answer:</td></tr><tr><td>MuSiQue</td><td>Answer the question based on the given passages. Only give me the answer and do not output any other words. If the question cannot be answered based on the information in the article, write “unanswerable”. The following are given passages. {context} Answer the question based on the given passages. Only give me the answer and do not output any other words. If the question cannot be answered based on the information in the article, write “unanswerable”. Question: {input} answer:</td></tr><tr><td>QMSum</td><td>You are given a meeting transcript and a query containing a question or instruction. Answer the query in one or more sentences. If the question cannot be answered based on the information in the article, write “unanswerable”. Transcript: {context} Now, answer the query based on the above meeting transcript in one or more sentences. If the question cannot be answered based on the information in the article, write “unanswerable”. Query: {input} Answer:</td></tr><tr><td>EN.QA</td><td>Read the book and answer the question. Be very concise in your answer. If the question cannot be answered based on the information in the article, write “unanswerable”. {context} Question: {input} Only give me the answer and do not output any other words. If the question cannot be answered based on the information in the article, write “unanswerable”. Answer:</td></tr><tr><td>EN.MC</td><td>Read the book and answer the question. If the question cannot be answered based on the information in the article, write “unanswerable”. {context} Question: {input} {all_classes} Only output the letter of the correct answer and do not output any other words. If the question cannot be answered based on the information in the article, write “unanswerable”. The letter of the correct answer is</td></tr></table>

Table 9: Prompts for each dataset.