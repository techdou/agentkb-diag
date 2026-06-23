# MuRAG: Multimodal Retrieval-Augmented Generator for Open Question Answering over Images and Text

Wenhu Chen, Hexiang Hu, Xi Chen, Pat Verga, William W. Cohen

Google Research

{wenhuchen,hexiang,patverga,wcohen}@google.com

## Abstract

While language Models store a massive amount of world knowledge implicitly in their parameters, even very large models often fail to encode information about rare entities and events, while incurring huge computational costs. Recently, retrieval-augmented models, such as REALM, RAG, and RETRO, have incorporated world knowledge into language generation by leveraging an external nonparametric index and have demonstrated impressive performance with constrained model sizes. However, these methods are restricted to retrieving only textual knowledge, neglecting the ubiquitous amount of knowledge in other modalities like images – much of which contains information not covered by any text. To address this limitation, we propose the first Multimodal Retrieval-Augmented Transformer (MuRAG), which accesses an external non-parametric multimodal memory to augment language generation. MuRAG is pretrained with a mixture of large-scale imagetext and text-only corpora using a joint contrastive and generative loss. We perform experiments on two different datasets that require retrieving and reasoning over both images and text to answer a given query: WebQA, and MultimodalQA. Our results show that MuRAG achieves state-of-the-art accuracy, outperforming existing models by 10- 20% absolute on both datasets and under both distractor and full-wiki settings.

## 1 Introduction

Pre-trained language models like GPT-3 (Brown et al., 2020), PaLM (Chowdhery et al., 2022), etc have been shown to capture a massive amount of world knowledge implicitly in their parameters. However, using such large models incurs an extremely high computation cost. As an alternative to a singular monolithic transformer, retrievalaugmented architectures like KNN-LM (Khandelwal et al., 2019), REALM (Guu et al., 2020),

## Visual information-seeking Queries

![](images/8d28cd0b0b54b80f5371ad996bfa7824242fb1e5b0f376058a35caf73dec01bd.jpg)  
Figure 1: Visual information-seeking queries: These queries are unanswerable with text-only retrieval and require retrieving and reasoning over images.

RAG (Lewis et al., 2020), FiD (Izacard and Grave, 2021), and RETRO (Borgeaud et al., 2021) have been proposed to decouple world knowledge from the model’s parameters. More specifically, these models are trained to access an external memory to enhance the model’s predictions. Such retrieval-augmented architectures have multiple beneficial properties including: decreased model size (Borgeaud et al., 2021), better attribution/- explanation for model predictions (Lewis et al., 2020), and adaptability to new information without retraining (Verga et al., 2021). However, previous retrieval-augmented models are limited to memories that contain only text or structured data and hence cannot make use of the massive amount of multimodal knowledge available on the web— much of which contains information only available in non-text modalities.

Figure 1, shows several information-seeking queries that require retrieving and reasoning over visual knowledge. Here, a user first poses a question such as “What can be found on the White House balconies at Christmas”. The system then retrieves relevant items from its memory, for example, the first image of Figure 1 with the caption “White House during Christmas”, which it uses to produce the answer “wreaths and garlands”. Existing text retrieval-augmented models would struggle with such queries because, in many cases, they would simply not have access to the answer as some knowledge does not exist in text form. That, coupled with the abundance of multimodal knowledge that exists, leads to the conclusion that retrievalaugmented models should ultimately be developed to retrieve and reason over multiple modalities.

![](images/94fb163a8d0cc550f9785874b0fa03b818a7852af7c2db9fe9fabdb12c7f4e7e.jpg)  
Figure 2: Model Overview: retrieval-and-predict pro cess of MuRAG on downstream datasets.

In this paper, we are specifically interested in endowing pre-trained language models with a nonparametric multimodal memory containing images, text, or image-text pairs. To accomplish this, we first combine pre-trained T5 (Raffel et al., 2020) and ViT (Dosovitskiy et al., 2020) models to build a backbone encoder (Figure 3), which encodes image-text pairs, image-only, and text-only inputs into a multimodal representation. MuRAG uses the backbone encoder to embed items into an external memory as well as queries to retrieve multimodal knowledge from that memory. These retrievals then augment a language model to generate more visually-grounded outputs.

We pre-train MuRAG with a mixture of image-text and text-only datasets including LAION (Schuhmann et al., 2021), Conceptual-Caption (Sharma et al., 2018), VQA (Antol et al., 2015) and Probably-Asked-Questions (PAQ) (Lewis et al., 2021). More specifically, we reformulate these datasets in a retrieve-and-predict format. Here, the model’s input is an image along with a text prompt. The model then retrieves from a memory containing captions and passages, which it uses to generate a target token sequence. The model is trained with both a contrastive and a generative loss; this teaches the model to discriminate relevant from irrelevant memory entries, and guides the model to leverage the multimodal knowledge into generation.

Unlike the pre-training stage, during finetuning Figure 2 the model’s input is a question, and the memory contains a collection of captioned images and text snippets. We fine-tune MuRAG on the downstream datasets with a contrastive and generative loss similar to pre-training. To avoid excessive computation cost, we develop a two-stage training pipeline to first train with small in-batch memory, and then with a statically encoded and indexed large global memory.

Our experiments show that MuRAG achieves state-of-the-art performance on two different openmultimodal-QA datasets, both of which require retrieving images and text from a large corpus to answer factoid questions: WebQA (Chang et al., 2022) and MultimodalQA (Talmor et al., 2021). On both datasets, we outperform sophisticated baselines (Li et al., 2020; Radford et al., 2021; Zhang et al., 2021) by 10-20% accuracy under both distractor (from 40+ candidates) and full-wiki settings (from 1M candidates). We also perform a comprehensive study to ablate different components of the pre-training to see their contributions. These empirical results demonstrate the effectiveness of our proposed models to integrate multimodal knowledge into pre-trained generation models and pave the way to unified retrieval-augmented frameworks.

## 2 Related Work

Retrieval Augmented Models Retrieval augmented models are hybrid models containing both parameterized sequence models and a nonparametric memory, infusing world knowledge into existing language models. Among them, KNN-LM (Khandelwal et al., 2019) was first proposed to retrieve instances from a text training corpus to help language modeling. Later, RETRO (Borgeaud et al., 2021) was proposed to scale up the text corpus to trillions of tokens, enabling the model to achieve similar perplexity to GPT-3 (Brown et al., 2020) with 25x fewer model parameters. Another family of models, such as REALM (Guu et al., 2020), RAG (Lewis et al., 2020), and FiD (Izacard and Grave, 2021), integrate Wikipedia passages as a datastore to benefit downstream knowledge intensive tasks (e.g. Question Answering). REALM is an encoder-only model trained with masked language modeling, while RAG and FiD adopt an encoder-decoder model with a generative language modeling objective. Compared to them, MuRAG is the first retrieval-augmented model that is capable of using knowledge presented in multiple modalities (i.e. visual and textual knowledge data), whereas all prior methods are restricted to using text-only knowledge.

Multimodal Transformers Multimodal transformers have demonstrated strong performances in learning cross-modal representation that are generally beneficial on downstream vision and language tasks, such as image-text retrieval (Karpathy and Fei-Fei, 2015), image captioning (Chen et al., 2015), and VQA (Antol et al., 2015). These methods typically learn a joint transformer model on top of unimodal visual and textual backbones, via fusing deep features from each modality. The early version of multimodal transformers (Lu et al., 2019; Chen et al., 2020; Li et al., 2020) usually learns a Transformer on pre-extracted unimodal features for contextualization, which makes it impossible to adjust those unimodal features to the target tasks. Recently, SimVLM (Wang et al., 2022) and COCA (Yu et al., 2022) proposed end-to-end training for both deep multimodal transformers and unimodal featurization networks and demonstrated strong performance in both multimodal and unimodal downstream tasks. The multimodal memory encoder of MuRAG is broadly similar to SimVLM and CoCa, but has a different focus to encode and retrieve multimodal knowledge (i.e. images and texts) to augment language generation models.

Multimodal Question Answering The problem of multimodal question answering has been extensively studied. VQA was the first proposed to answer questions from visual-only inputs. Later, OK-VQA (Marino et al., 2019) enlarged VQA’s scope to annotate questions requiring both image and implicit textual/common-sense knowledge to answer. More recently, MuMuQA (Reddy et al., 2021), ManyModelQA (Hannan et al., 2020) and MIMOQA (Singh et al., 2021) provide questions which require reasoning over images and explicitly provided text snippets. However, these datasets are restricted to dealing with given text and images without requiring any retrieval from the web: they are analogous to machine-reading approaches to QA from text like SQuAD, rather than open-book QA. To study the more realistic open multimodal QA task, WebQA (Chang et al., 2022) and MultimodalQA (Talmor et al., 2021) have been proposed to evaluate answers to open queries which require retrieving and reasoning over a large-scale web multimodal corpus. Our model uses these datasets to study open-world multimodal question answering, obtaining state-of-the-art results.

## 3 Model

## 3.1 Backbone Encoder

![](images/ab78faabe3de1111738969533fe81317ca02a63994c69c8975b7478b7d92dd74.jpg)  
Figure 3: Backbone encoder: ViT encodes image patches into a sequence of vectors $\mathbf { e } _ { I } ,$ while word embedding converts text tokens into another sequence of vectors ${ \bf e } _ { T }$ . These vectors are concatenated to form $f _ { \theta } ( e )$ and fed to a decoder for text generation.

MuRAG is built on top of a simpler model we call a “backbone” model, which is pre-trained to encode image-text pairs such that they are suitable for both answer generation and retrieval. The backbone model’s encoder is used as a component of the MuRAG model. The backbone model is built with a pre-trained visual Transformer (Dosovitskiy et al., 2020) and a T5 text Transformer (Raffel et al., 2020), and consists of a multimodal encoder $f _ { \theta }$ and decoder g<sub>θ</sub>. The encoder takes as input a sequence of image-text pairs, where either the image or the text component can be empty to accommodate textonly and image-only cases.

As depicted in Figure 3, the encoder can take a sequence of images and text. For image input, we first split each into 16x16 patches and feed them to a ViT (Dosovitskiy et al., 2020) transformer to generate a sequence of visual embedding denoted as $\mathbf { e } _ { I } \in \mathbb { R } ^ { L _ { i } \times D }$ , where $L _ { i }$ is the length of the image tokens. For text input, we use word embedding to produce another sequence of textual embedding $\mathbf { e } _ { T } \in \mathbb { R } ^ { L _ { t } \times D }$ . For k images and n text inputs, we concatenate all their embeddings in the input order as $\mathbf { e } = [ \mathbf { e } _ { I } ^ { 1 } ; \mathbf { e } _ { T } ^ { 1 } ; \dots ; \mathbf { e } _ { I } ^ { k } ; \mathbf { e } _ { T } ^ { n } ] ^ { \top } \in \mathbb { R } ^ { ( k L _ { t } + n \bar { L } _ { i } ) \times D } ,$ which is fed to another bi-directional transformer $f _ { \theta }$ initialized from T5. We enable cross-attention between the two modalities to produce a fused representation, denoted as $f _ { \theta } ( \mathbf { e } ) ^ { } \in \mathbb { R } ^ { ( k L _ { t } + n L _ { i } ) \times \hat { D } }$ We add a [CLS] token to obtain a pooled representation $f _ { \theta } ( \mathbf { e } ) _ { \mathrm { [ C L S ] } } \in \mathbb { R } ^ { D }$ for dense retrieval.

## 3.2 MuRAG

We build MuRAG (shown in Figure 4) on top of the backbone model. During the retriever stage, MuRAG takes a query q of any modality as input and retrieves from a memory M of image-text pairs. Specifically, we apply the backbone encoder $f _ { \theta }$ to encode a query q, and use maximum inner product search (MIPS (Guo et al., 2020)) over all of the memory candidates $m \in \mathcal { M }$ to find the Top-K nearest neighbors $T o p _ { K } ( \mathcal { M } | q ) = [ m _ { 1 } , \cdot \cdot \cdot , m _ { k } ]$ Formally, we define $T o p _ { K } ( \mathcal { M } | q )$ as follows:

$$
T o p _ {K} (\mathcal {M} | q) = \underset {m \in \mathcal {M}} {T o p K} f _ {\theta} (q) _ {[ \mathrm{CLS} ]} \cdot f _ {\theta} (m) _ {[ \mathrm{CLS} ]}
$$

During the reader stage, the retrievals (the raw image patches) are combined with the query q as an augmented input $[ m _ { 1 } , \cdot \cdot \cdot , m _ { k } , q ]$ , which is fed to the backbone encoder $f _ { \theta }$ to produce retrievalaugmented encoding. The decoder model $g _ { \boldsymbol { \theta } }$ uses attention over this representation to generate textual outputs ${ \bf y } = y _ { 1 } , \cdots , y _ { n }$ token by token.

$$
p (y _ {i} | y _ {i - 1}) = g _ {\theta} (y _ {i} | f _ {\theta} (T o p _ {K} (\mathcal {M} | q); q); y _ {1: i - 1})
$$

where y is decoded from a given vocabulary V.

## 3.3 Pre-training

The pre-training implementation is depicted in the upper portion of Figure 4, where the input query is an image $x _ { I }$ plus a text prompt $x _ { p }$ . The external memory M contains textual-only entries $m ^ { T }$ The Top-K retrievals $m _ { 1 } ^ { T } , \cdots , m _ { k } ^ { T }$ are leveraged to generate the textual output. To avoid the excessive computation cost of backpropagation over the massive external memory, we adopt an in-batch memory $\mathcal { M } _ { B }$ , dynamically constructed from the input examples in a batch. The small in-batch memory enables MuRAG to continuously update the memory encoder efficiently similar to TOME (de Jong et al., 2022) and QAMAT (Chen et al., 2022).

Dataset The pre-training corpus consists of LAION (Schuhmann et al., 2021), Conceptual-Caption-12M+3M (CC) (Sharma et al., 2018; Changpinyo et al., 2021), VQA (Antol et al., 2015) and PAQ (Lewis et al., 2021) Table 1. LAION is a publicly-released image-text dataset containing crawled image-text pairs filtered by CLIP (Radford et al., 2021). We apply rules to filter LAION from 400M to 200M by removing text with HTTP-URLs or image width/height beyond 1000 pixels. CC contains 15M (image, anonymized alt-text) pairs crawled from the web but filtered more extensively to maintain high alignment quality. VQA contains annotated QA pairs aligned to MSCOCO images. We further add captions to each image from MSCOCO-Captioning (Lin et al., 2014) to create (Image, Caption, QA) triples. PAQ is a textonly dataset containing 65M machine-generated QA pairs along with their source Wikipedia passage.

<table><tr><td>Dataset</td><td>#Size</td><td>Format</td><td>Source</td></tr><tr><td>CC</td><td>15M</td><td>(Image, Caption)</td><td>Crawled</td></tr><tr><td>LAION</td><td>200M</td><td>(Image, Alt-Text)</td><td>Crawled</td></tr><tr><td>PAQ</td><td>65M</td><td>(Passage, QA)</td><td>Generated</td></tr><tr><td>VQA</td><td>400K</td><td>(Image, Caption, QA)</td><td>Annotated</td></tr></table>

Table 1: Pre-training Dataset Statistics

For LAION and CC, we use the input image as $x _ { I }$ , and ‘generate caption:’ as the text prompt $x _ { p }$ For VQA, we use the input image as $x _ { I }$ and the question as the prompt $x _ { p } .$ . For PAQ, we use an empty array as the input image and the question as the prompt. The in-batch memory $\mathcal { M } _ { B }$ is constructed by stacking the captions associated with the input images in LAION/CC/VQA and the passages associated with the questions in PAQ. Each textual memory entry is denoted as $m ^ { T }$ . The decoder is optimized to generate either a caption or an answer, depending on the source dataset. Since the four dataset sizes are highly unbalanced, we use fixed mixture sampling ratios to balance their presence during pre-training.

We train the model with a joint loss $L = L _ { g e n } +$ $L _ { c o n }$ as follows:

$$
\begin{array}{l} L _ {c o n} = - \log \frac {e x p (f _ {\theta} (x _ {I} , x _ {p}) \cdot f _ {\theta} (m ^ {T}))}{\sum_ {m \in \mathcal {M} _ {B}} e x p (f _ {\theta} (x _ {I} , x _ {p}) \cdot f _ {\theta} (m ^ {T}))} \\ L _ {g e n} = - \log g _ {\theta} (\mathbf {y} | f _ {\theta} (M _ {p}; x _ {I}; x _ {p})) \\ M _ {p} = \left\{ \begin{array}{l l} T o p _ {K} (\mathcal {M} _ {B} | x _ {I}, x _ {p}) & \text { If } (x _ {I}, x _ {p}) \in \text { PAQ / VQA } \\ \emptyset & \text { If } (x _ {I}, x _ {p}) \in \text { LAION / CC } \end{array} \right. \end{array}
$$

where $M _ { p }$ is the retrieved augmentation: if the input query is from PAQ/VQA, we use the retrieved memory entries, otherwise, we use null. The reason for setting it to null for LAION/CC is to avoid a trivial solution when the generation target (caption) also exactly appears in the memory.

The contrastive loss $L _ { c o n }$ is minimized to discriminate between the positive query-memory pairs on the in-batch memory $\mathcal { M } _ { B }$ as follows:

Pre-Training Stage: Query is (Image, Text) Pair, Memory is Text, the output the text  
![](images/658fe4d332be334548a34b9f40b8a955a6553a9d86cc812fa3479230bba4164b.jpg)

Fine-Tune Stage: Query is text, Memory is (Image, Text) Pairs, the output is text  
![](images/16ebd9dce116a85a1efcdba4b136a1da43649f56e2e01cc226d207f8d23bcd29.jpg)  
Figure 4: Model Architecture: the model accesses an external memory to obtain multimodal knowledge contained in images or text snippets, which is used to augment the generation. The upper part defines the pre-training implementation, while the lower part defines fine-tuning implementation.

and all other query-memory pairs from the memory. The pairwise matching score is computed as the dot product between query $f _ { \theta } ( x _ { I } ; x _ { p } ) _ { \mathrm { [ C L S ] } }$ and candidates $f _ { \boldsymbol { \theta } } ( m ^ { T } ) _ { \mathrm { [ C L S ] } }$ . This objective enables the model to retrieve the most relevant knowledge from the memory. The generative loss $L _ { g e n }$ is minimized to generate target tokens y conditioned on the retrieval-augmented representation. This objective enables the model to combine information across different modalities for text generation.

## 3.4 Fine-tuning

We finetune MuRAG to align with the expected inputs of the downstream datasets which require answering text questions by retrieving image-caption pairs or text snippets from the external knowledge datastore. As depicted in the lower part of Figure 4, the input query for the downstream task is a text question $x _ { q } ,$ , and the memory M containing (image, text) pairs $( m ^ { I } , m ^ { T } ) .$ <sup>1</sup> The Top-K retrievals $\{ \bar { ( } m _ { 1 } ^ { I } , m _ { 1 } ^ { T } \bar { ) } , \cdot \cdot \cdot , ( m _ { k } ^ { I } , m _ { k } ^ { T } ) \}$ } are leveraged to generate the answer a. To minimize the computation cost, we develop a two-stage pipeline to optimize with an in-batch memory and then resume with fixed retrieval from global memory.

In-Batch Training In this stage, we aim to minimize the joint loss function ${ \cal L } = { \cal L } _ { c o n } + { \cal L } _ { g e n }$ based

$$
\begin{array}{l} L _ {c o n} = - \log \frac {e x p (f _ {\theta} (x _ {q}) \cdot f _ {\theta} (m ^ {I} ; m ^ {T}))}{\sum_ {m \in \mathcal {M} _ {B}} e x p (f _ {\theta} (x _ {q}) \cdot f _ {\theta} (m ^ {I} ; m ^ {T}))} \\ L _ {g e n} = - \log g _ {\theta} (\mathbf {y} | f _ {\theta} (T o p _ {K} (\mathcal {M} _ {B} | x _ {q}); x _ {q})) \end{array}
$$

The in-batch memory $\mathcal { M } _ { B }$ is constructed in the following way: the k-th example in the dataset is represented as $( x _ { q , k } , y _ { k } , \{ m _ { i } ^ { I } , \bar { m } _ { i } ^ { I } \} _ { k } , \{ \bar { m } _ { j } ^ { I } , \bar { m } _ { j } ^ { T } \} _ { k } )$ where m represents the positive (image, text) source, and m¯ represents the hard negative (image, text) source provided by the dataset<sup>2</sup>. For a batch with B examples, we assemble all the associated positive and negative knowledge source as our in-batch memory $\mathcal { M } _ { B }$ = $\{ \{ m _ { i } ^ { I } , m _ { i } ^ { I } \} _ { 1 } , \{ \bar { m } _ { j } ^ { I } , \bar { m } _ { j } ^ { T } \} _ { 1 } , \cdot \cdot \cdot , \{ \bar { m } _ { j } ^ { I } , \bar { m } _ { j } ^ { T } \} _ { B } \}$

Fixed-Retrieval Training After in-batch training, we encode all available cross-modal pairs, and index these encodings for fast MIPS retrieval. We then apply the trained retriever to search over the full multimodal corpus M to obtain the global top-K retrievals $T o p _ { K } ( \mathcal { M } | x _ { q } )$ and continue to optimize $L _ { g e n }$ . During this training phase, the stored encodings are not updated. During inference time, we use fixed encodings to generate the answers.

## 4 Experiments

## 4.1 Implementation Details

The backbone model uses T5-base (Raffel et al., 2020) and a ViT-large model (Dosovitskiy et al., 2020) as described in Table 2. We adopt the sentence-piece model from T5 with a vocabulary size of 32128. The ViT model was pre-trained on the JFT dataset. We resize every image into 224x224 pixels and split them into a sequence of 16x16 patches. The output of ViT is a sequence of 1024-dimension vectors, which are projected to 768-dimension for consistency with T5 model. MuRAG reuses the model as retriever and reader, thus the full model size is 527M parameters.

<table><tr><td>Model</td><td>#Enc</td><td>#Dec</td><td>Hidden</td><td>Heads</td><td>Params</td></tr><tr><td>ViT-large</td><td>24</td><td>0</td><td>1024</td><td>16</td><td>307M</td></tr><tr><td>T5-base</td><td>12</td><td>12</td><td>768</td><td>12</td><td>220M</td></tr></table>

Table 2: The model size and configurations, with #Enc/#Dec denoting encoder/decoder layers.

Our model is implemented in JAX (Bradbury et al., 2018), based on the T5X codebase (Roberts et al., 2022). During pre-training, we first train the model on LAION for 1M steps, and then continue training on CC/PAQ/VQA with 1:1:1 sample ratio for another 200K steps. We optimize the model with Adafactor (Shazeer and Stern, 2018). For both stages, we adopt a constant learning rate of 5e-4 and a batch size of 4096. The models are trained on 64 Cloud v4 TPUs (Jouppi et al., 2020).

We then fine-tune MuRAG on WebQA and MultimodalQA with a constant learning rate of 3e-4 for 20K steps. The checkpoint with the highest validation score is run on the test set. We use a batch size of 64 and set TopK=4 for both in-batch training and fixed-retrieval training. We noticed that increasing Top-K further does not yield further improvement. We use a beam size of 2 to search for the best hypothesis for both datasets (increasing it further doesn’t yield better performance).

## 4.2 Datasets

For evaluation, we choose two multimodal QA datasets: WebQA (Chang et al., 2022) and MultimodalQA (Talmor et al., 2021) and demonstrate their statistics in Table 3.

WebQA This dataset contains multi-hop, multimodal question-answer pairs where all questions are knowledge-seeking queries. The queries require 1-2 images or 1-2 text snippets to answer.

<table><tr><td>Dataset</td><td>Train Image/Text</td><td>Dev Image/Text</td><td>Test Image/Text</td></tr><tr><td>WebQA</td><td>18K/17K</td><td>2.5K/2.4K</td><td>3.4K/4K</td></tr><tr><td>MultimodalQA</td><td>2.1K/7.4K</td><td>230/721</td><td>-</td></tr></table>

Table 3: Overall Statistics of downstream dataset.

Each query in WebQA is associated with a set of visual/text distractors (hard negatives). The answers in WebQA are normally complete sentences to better assess the model’s generation capability. Two evaluation setups are used, namely distractor and full-wiki. Under the distractor setup, the model needs to retrieve from these hard negatives + positives to answer the question. Under the full-wiki setup, the model needs to search over 1.1M text and visual sources from Wikipedia to answer the question. For evaluation, WebQA uses BARTScore (Yuan et al., 2021) to measure the fluency between the generation and the reference, and keyword accuracy score to measure the correctness/truthfulness of the generation. These two scores are multiplied to calculate the overall score.

MultimodalQA-Subset This dataset contains human-annotated multimodal questions over different modalities including tables, text, and images. Wikipedia tables are used as anchors to connect different modalities. The authors first use the template to generate questions and then ask crowd-workers to filter and paraphrase the generated questions. Since tables are outside the scope of our paper, we focus on the subset of queries requiring only text and image information. Specifically, we choose the questions with types of ‘TextQ’ and ‘ImageQ’ to construct the subset. The query requires 1 image or 1 text snippet to answer. Each query in MultimodalQA is also associated with visual and text distractors (hard negatives). Similarly, two evaluation setups are used as before. Under a full-wiki setup, MultimodalQA uses a database containing 500K text and visual sources. The evaluation scores are based on Exact Match and F1.

## 4.3 Baselines

For WebQA and MultimodalQA, we mainly compare different variants of pre-trained visionlanguage models.

VLP In WebQA, VLP-like models (Zhou et al., 2020) like Oscar (Li et al., 2020) and VinvL (Zhang et al., 2021) are used as the standard baselines. These models were pre-trained on Conceptual

3M (Sharma et al., 2018) with a masked language objective. During fine-tuning, the VLP model takes a set of token inputs <[CLS], s<sub>i</sub>, [SEP], Q, [SEP]> first to select the most plausible source $s _ { i } ,$ and then feed $s _ { i }$ in the form of <[CLS], S, Q, A, [SEP]> to autoregressively decode answer A with masked language model prediction.

AutoRouting In MultimodalQA, this method first applies a question type classifier to detect the modality of the question (either a passage or an image), and then routes the question to its submodel. The method uses RoBERTa-large (Roberts et al., 2022) for text-questions and VilBERT (Lu et al., 2019) with features extracted from Faster-RCNN (Ren et al., 2015) for image questions.

CLIP (K) CLIP (Radford et al., 2021) is used for full-wiki retrieval. Specifically, the baselines systems adopt CLIP to encode queries and all the image/text candidates separately into vectors and then run approximated nearest neighbor searches to find a set of K potential candidates. After the coarselevel retrieval without cross-attention, it adopts a reranker to further narrow down to the 1-2 candidates to feed as input S to the QA model.

## 4.4 Experimental Results

We demonstrate WebQA’s results in Table 4. All results reported are the medium score from three runs with different random seeds, and the variance of the Overall score is within 0.2%. We can observe that MuRAG can significantly outperform VLP with different backends including Oscar, ResNet, and VinVL. In retrieval performance, our model outperforms VLP by 15% in the full-wiki setting. For Fluency, our model outperforms VLP by 12% under the distractor setting and 14% under the fullwiki setting. For Accuracy, our model manages to achieve 16% under the distractor setting and even 20% the under the full-wiki setting. These improvements reflect the high fluency and accuracy of MuRAG’s generation, and the improvement is more pronounced for full wiki.

We show the MultimodalQA results in Table 5. We can see that MuRAG is also able to vastly outperform the routing-based multimodality QA model. For text questions, our model improves over AutoRouting by 10+% EM under both settings. For image questions, the gap becomes more significant, with 20+% improvement under both settings. Similarly, we find that our model is more capable of handling full-wiki corpus.

<table><tr><td rowspan="2">Evaluation Metrics</td><td colspan="4">Distractor</td></tr><tr><td>Retr</td><td>FL</td><td>Accuracy</td><td>Overall</td></tr><tr><td>Question-Only</td><td>-</td><td>34.9</td><td>22.2</td><td>13.4</td></tr><tr><td>VLP (Oscar)</td><td>68.9</td><td>42.6</td><td>36.7</td><td>22.6</td></tr><tr><td>VLP + ResNeXt</td><td>69.0</td><td>43.0</td><td>37.0</td><td>23.0</td></tr><tr><td>VLP + VinVL</td><td>70.9</td><td>44.2</td><td>38.9</td><td>24.1</td></tr><tr><td>MuRAG</td><td>74.6</td><td>55.7</td><td>54.6</td><td>36.1</td></tr><tr><td>Evaluation</td><td colspan="4">Full-Wiki</td></tr><tr><td>CLIP (2) + VLP</td><td>11.9</td><td>34.2</td><td>24.1</td><td>14.6</td></tr><tr><td>CLIP (20) + VLP</td><td>24.0</td><td>36.1</td><td>27.2</td><td>16.1</td></tr><tr><td>MuRAG</td><td>39.7</td><td>50.7</td><td>47.8</td><td>31.5</td></tr></table>

Table 4: WebQA official test-set results indicated on leaderboard<sup>3</sup> as of May 2022. Retr denotes the retrieval-F1 score. FL refers to fluency metric BARTSCcore, and Accuracy refers to keyword matching F1 score, they are combined as Overall.

<table><tr><td rowspan="3">EvaluationMetrics</td><td colspan="5">Distractor</td></tr><tr><td colspan="2">Text</td><td colspan="2">Image</td><td rowspan="2">All EM</td></tr><tr><td>EM</td><td>F1</td><td>EM</td><td>F1</td></tr><tr><td rowspan="2">Question-Only AutoRouting</td><td>15.4</td><td>18.4</td><td>11.0</td><td>15.6</td><td>13.8</td></tr><tr><td>49.5</td><td>56.9</td><td>37.8</td><td>37.8</td><td>46.6</td></tr><tr><td>MuRAG</td><td>60.8</td><td>67.5</td><td>58.2</td><td>58.2</td><td>60.2</td></tr><tr><td rowspan="3">EvaluationMetrics</td><td colspan="5">Full-Wiki</td></tr><tr><td colspan="2">Text</td><td colspan="2">Image</td><td rowspan="2">All EM</td></tr><tr><td>EM</td><td>F1</td><td>EM</td><td>F1</td></tr><tr><td>CLIP (10) + AutoRouting</td><td>35.6</td><td>40.2</td><td>32.5</td><td>32.5</td><td>34.7</td></tr><tr><td>MuRAG</td><td>49.7</td><td>56.1</td><td>56.5</td><td>56.5</td><td>51.4</td></tr></table>

Table 5: Multimodal dev-set results on the subset.

## 4.5 Ablation Study

Here we ablate the properties of MuRAG to better understand our experimental results.

Pre-training Corpus In order to study the contributions of different pre-training corpora, we investigated several pre-training corpus combinations. We report their fine-tuned results on WebQA test set in Table 6. As can be seen, without any pre-training, our model only achieves an overall score of 23.5, which lags behind the baseline models. After pretraining on different singular datasets, MuRAG is able to achieve better performance than the baselines. Among the individual datasets, LAION is shown to yield the highest score, and adding CC, PAQ, and VQA to the pre-training corpus set one by one produces steady improvements.

Two-Stage Fine-tuning In order to study the necessity of the two-stage fine-tuning, we perform an ablation study to see the impact of the two stages. We display our results in Table 7. (Only In-Batch)

<table><tr><td>Pre-train Dataset</td><td>FL</td><td>Accuracy</td><td>Overall</td></tr><tr><td>None</td><td>42.5</td><td>36.1</td><td>23.5</td></tr><tr><td>CC</td><td>46.4</td><td>41.3</td><td>25.6</td></tr><tr><td>LAION</td><td>47.8</td><td>44.8</td><td>28.3</td></tr><tr><td>VQA</td><td>47.0</td><td>44.4</td><td>27.4</td></tr><tr><td>PAQ</td><td>46.8</td><td>42.8</td><td>27.0</td></tr><tr><td>LAION+CC</td><td>49.5</td><td>47.4</td><td>30.7</td></tr><tr><td>LAION+CC+PAQ</td><td>53.7</td><td>51.8</td><td>34.4</td></tr><tr><td>LAION+CC+PAQ+VQA</td><td>55.7</td><td>54.6</td><td>36.1</td></tr></table>

Table 6: Ablation Study for different pre-training corpus, score under distractor setting.

<table><tr><td>Model</td><td>WebQA</td><td>Multimodal</td></tr><tr><td>MuRAG (Only In-Batch)</td><td>29.4</td><td>49.6</td></tr><tr><td>MuRAG (Only Fixed-Retrieval)</td><td>25.8</td><td>40.7</td></tr><tr><td>MuRAG (Two Stage)</td><td>31.5</td><td>51.4</td></tr></table>

Table 7: Ablation Study for different fine-tuning stages to see their contributions. WebQA uses the overall score, and MultimodalQA refers to EM-all score.

<table><tr><td>Evaluation</td><td>Model</td><td>Correct</td><td>Wrong</td></tr><tr><td rowspan="2">Distractor</td><td>MuRAG (Text)</td><td>80%</td><td>20%</td></tr><tr><td>MuRAG (Image)</td><td>64%</td><td>36%</td></tr><tr><td rowspan="2">Full-Wiki</td><td>MuRAG (Text)</td><td>72%</td><td>28%</td></tr><tr><td>MuRAG (Image)</td><td>54%</td><td>46%</td></tr></table>

Table 8: The human evaluation results on WebQA dataset separately for image/text queries.  
Waterpark in Ayia Napa ...

refers to the model trained only with in-batch memory are directly used to generate outputs by accessing the global memory. Without further tuning, the performance will drop by roughly 2% on both datasets. (Only Fixed-Retrieval) refers to using the pre-trained retriever directly to obtain Top-K and then optimize the generative loss. As can be seen, the performance drop is more severe in this case for both datasets. This is understandable due the misalignment between pre-training retrieval is (image + text->text) while the fine-tuning retrieval is (text -> image+text). Thus, it is necessary to adapt the MuRAG’s pre-trained retriever to different use cases depending on the downstream datasets.

## 4.6 Human Analysis

In order to better understand the model’s performance, we manually study 200 model outputs and classify them into three categories and show our manual analysis results in Table 8. As can be seen, image queries are much harder than text queries. MuRAG only achieves 64% accuracy for the distractor setting and 54% accuracy for the full-wiki setting, falling significantly behind text accuracy.

We further categorize the image-query errors

![](images/08cdf1c4ab5cb0a8da5ddb64b17ebfb3bd27e597fd1c7a15e176523d29af669c.jpg)  
Facade of Grand Palais, Paris 9

![](images/2df480c21e6a5b3c9fd42899db8621d3a4e509c1e9d4faa20773c62e261f2d23.jpg)  
Q: At the waterpark in Ayia Napa, are there waterslides that are taller than trees? P: Yes, at the waterpark in Ayia Napa there are waterslides that are taller than trees. R: Yes. there are waterslides taller than trees.  
How many spaces for banner flags to be hung are there between the columns on the Grand Palais? There are three spaces for banner flags to be hung.

Museum exhibits IMNH exhibit in located in Pocatello Idaho.  
Museum of international folk art display Display at the ..  
![](images/09c5d1b6d4da7db75493b9495e5ddc2de9789907d21206624a2d441308f4dde3.jpg)

![](images/79e4d1caa6b4f848a5467743d883e492c572e3232c5ba5fc3c7a36fe333cd8b8.jpg)  
Q: What kind of lighting is on the ceiling at the Museum of International Folk Art in Santa Fe and the IMNH exhibit in Pocatello Idaho?  
P: Track lighting is on the ceiling at the Museum of International Folk Art in Santa Fe and the IMNH exhibit in Pocatello Idaho. R: Spot lights are on the ceiling.

Figure 5: Upper left: correct prediction, Upper Right: error due to miscounting, Lower: error due to misrecognition (multiple image reasoning). Q refers to the question, P refers to prediction and R refers to the reference.

manually into the categories of Table 9. Counting is the most difficult question type, and constitutes 52% of the total errors, while object recognition errors rank second, constituting 29% of errors. In contrast, identifying color, shape, and gender is comparatively easier, with fairly low error rates. We demonstrate some correct and typical error cases in Figure 5 including miscounting and misrecognizing objects. We observe that these errors are mostly due to several reasons: 1) the question is related to infrequent objects, thus making recognition errors, 2) the image scene is highly complex with a large number of objects, thus grounding to a specific region is difficult, 3) the questions require optical character recognition ability from images. Hence, the bottleneck of MuRAG is still in the visual understanding module.

<table><tr><td>Category</td><td>Count</td><td>Object</td><td>Color</td><td>Shape</td><td>Gender</td></tr><tr><td>Ratio</td><td>52%</td><td>29.4%</td><td>5.8%</td><td>5.8%</td><td>5.8%</td></tr></table>

Table 9: Error categorization and their ratios on sampled WebQA-dev image queries.

## 5 Examples

We list more examples in Figure 6 and Figure 7. As can be seen, in the first example, the model is grounded on the oracle image-text pair to make the correct prediction. However, in the second example, though the model retrieves the wrong imagetext pair, it is able to make the correct prediction of ‘the angel is holding a dead body’. We conjecture that the model utilizes textual clues to make the prediction rather than grounding on the image itself. Such shortcut learning is concerning and needs to be addressed through better learning algorithms.

Q: How many rows of keys are on the Hammond Aurora?  
Hammond Aurora.png Hammond Aurora ,custom,classic,century  
![](images/0be519582746db56afe52c910c1334fb9d99476adb1b8959538f12c0ae7e65d0.jpg)

Hammond Aurora.png Hammond Aurora ,custom,classic,century  
![](images/36ab2a0f330b68d5a7dfd01f021ed0a55fc966269c1777be31c24b1ec5fd450a.jpg)  
Answer: There are two rows of keys on the Hammond Aurora. Ref: There are two rows of keys on the Hammond Aurora.  
Figure 6: Examples: we demonstrate model retrieval vs. groundtruth and model answer vs. reference.

## 6 Conclusion

In this paper, we build the first visually-grounded language generator capable of retrieving multimodal knowledge from a large-scale corpus. Our experiments show the promise of this approach, as it outperforms existing baselines by a large margin. At the same time, the performance on knowledgeseeking queries that require reasoning over images is still significantly lower than the performance on queries requiring only text. This indicates that there is still ample room for further improvements and we hope our study can motivate more research on better multimodal retrieval-augmented models.

## Limitations

The current approach has several limitations: 1) since we do not mine hard negatives during pretraining, negatives come from other examples within the same batch. This requires that we set the batch size sufficiently large enough to collect hardenough negatives. This results in the pre-training requiring a large number of computation resources to reach competitive retrieval abilities. 2) our pretraining corpus’s format (image -> text) is different from fine-tuning (text -> image+text). This misalignment limits the model’s performance. Future work should consider how to design a betteraligned pre-training objective to achieve better performance. 3) Current visual representation in the reader stage is relatively expensive, i.e. 16x16=196 tokens per image, which poses great challenges for the transformer encoder to scale up to large Top-K values due to the quadratic attention complexity.

Q: In the statue in front of Berlin's Mitte cathedral, is the angel holding a dead or alive boy?  
Berlin.Dom The Berlin Cathedral, Berlin, Germany  
![](images/1f62c7350cac3168faea3003bdb2e3decc142b686a591660ae85f1d5109a8cd3.jpg)

Berlin, Germany (April 2016) - 063 Berlin, Germany (April 2016)  
![](images/fe0300f101aef3c9a035da7a39c2979d4da925fc32e0cf3a787bf55cda295c3d.jpg)  
Answer: The angel is holding a dead boy in the statue in front of Berlin's Mitte cathedral  
Ref: In the statue in front of Berlin's Mitte Cathedral, the angel is holding a dead boy.  
Figure 7: Examples: we demonstrate model retrieval vs. groundtruth, and model answer vs. reference.

## Ethical Statement

Our work uses the LAION dataset, a widely-used and publicly available large-scale visual-language corpus crawled from the web. The authors have conducted automatic filtering to greatly reduce harmful content. However, it is not possible to fully remove all of the potential risks from the data given its tremendous size. Being trained on this dataset, we anticipate our model to contain some biases (racial, gender, etc.). During our manual inspection, we saw some such biases, for example, 5% of errors are caused by misrecognition of gender. However, there are other many other forms of biases that we cannot fully enumerate or observe

explicitly.

## References

Stanislaw Antol, Aishwarya Agrawal, Jiasen Lu, Margaret Mitchell, Dhruv Batra, C Lawrence Zitnick, and Devi Parikh. 2015. Vqa: Visual question answering. In Proceedings of the IEEE international conference on computer vision, pages 2425–2433.

Sebastian Borgeaud, Arthur Mensch, Jordan Hoffmann, Trevor Cai, Eliza Rutherford, Katie Millican, George van den Driessche, Jean-Baptiste Lespiau, Bogdan Damoc, Aidan Clark, et al. 2021. Improving language models by retrieving from trillions of tokens. arXiv preprint arXiv:2112.04426.

James Bradbury, Roy Frostig, Peter Hawkins, Matthew James Johnson, Chris Leary, Dougal Maclaurin, George Necula, Adam Paszke, Jake VanderPlas, Skye Wanderman-Milne, and Qiao Zhang. 2018. JAX: composable transformations of Python+NumPy programs.

Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. 2020. Language models are few-shot learners. Advances in neural information processing systems, 33:1877–1901.

Yingshan Chang, Mridu Narang, Hisami Suzuki, Guihong Cao, Jianfeng Gao, and Yonatan Bisk. 2022. Webqa: Multihop and multimodal qa. The Conference on Computer Vision and Pattern Recognition.

Soravit Changpinyo, Piyush Sharma, Nan Ding, and Radu Soricut. 2021. Conceptual 12m: Pushing webscale image-text pre-training to recognize long-tail visual concepts. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 3558–3568.

Wenhu Chen, Pat Verga, Michiel de Jong, John Wieting, and William Cohen. 2022. Augmenting pre-trained language models with qa-memory for open-domain question answering. arXiv preprint arXiv:2204.04581.

Xinlei Chen, Hao Fang, Tsung-Yi Lin, Ramakrishna Vedantam, Saurabh Gupta, Piotr Dollár, and C Lawrence Zitnick. 2015. Microsoft coco captions: Data collection and evaluation server. arXiv preprint arXiv:1504.00325.

Yen-Chun Chen, Linjie Li, Licheng Yu, Ahmed El Kholy, Faisal Ahmed, Zhe Gan, Yu Cheng, and Jingjing Liu. 2020. Uniter: Universal image-text representation learning. In European conference on computer vision, pages 104–120. Springer.

Aakanksha Chowdhery, Sharan Narang, Jacob Devlin, Maarten Bosma, Gaurav Mishra, Adam Roberts, Paul Barham, Hyung Won Chung, Charles Sutton,

Sebastian Gehrmann, et al. 2022. Palm: Scaling language modeling with pathways. arXiv preprint arXiv:2204.02311.

Michiel de Jong, Yury Zemlyanskiy, Nicholas FitzGerald, Fei Sha, and William Cohen. 2022. Mention memory: incorporating textual knowledge into transformers through entity mention attention. ICLR.

Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, et al. 2020. An image is worth 16x16 words: Transformers for image recognition at scale. In International Conference on Learning Representations.

Ruiqi Guo, Philip Sun, Erik Lindgren, Quan Geng, David Simcha, Felix Chern, and Sanjiv Kumar. 2020. Accelerating large-scale inference with anisotropic vector quantization. In International Conference on Machine Learning, pages 3887–3896. PMLR.

Kelvin Guu, Kenton Lee, Zora Tung, Panupong Pasupat, and Mingwei Chang. 2020. Retrieval augmented language model pre-training. In Proceedings of the 37th International Conference on Machine Learning, volume 119 of Proceedings of Machine Learning Research, pages 3929–3938. PMLR.

Darryl Hannan, Akshay Jain, and Mohit Bansal. 2020. Manymodalqa: Modality disambiguation and qa over diverse inputs. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 34, pages 7879–7886.

Gautier Izacard and Édouard Grave. 2021. Leveraging passage retrieval with generative models for open domain question answering. In Proceedings of the 16th Conference of the European Chapter of the Association for Computational Linguistics: Main Volume, pages 874–880.

Norman P Jouppi, Doe Hyun Yoon, George Kurian, Sheng Li, Nishant Patil, James Laudon, Cliff Young, and David Patterson. 2020. A domain-specific supercomputer for training deep neural networks. Communications of the ACM, 63(7):67–78.

Andrej Karpathy and Li Fei-Fei. 2015. Deep visualsemantic alignments for generating image descriptions. In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 3128–3137.

Urvashi Khandelwal, Omer Levy, Dan Jurafsky, Luke Zettlemoyer, and Mike Lewis. 2019. Generalization through memorization: Nearest neighbor language models. In International Conference on Learning Representations.

Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, et al. 2020. Retrieval-augmented generation for knowledge-intensive nlp tasks. Advances in Neural Information Processing Systems, 33:9459–9474.

Patrick Lewis, Yuxiang Wu, Linqing Liu, Pasquale Minervini, Heinrich Küttler, Aleksandra Piktus, Pontus Stenetorp, and Sebastian Riedel. 2021. Paq: 65 million probably-asked questions and what you can do with them. Transactions of the Association for Computational Linguistics, 9:1098–1115.

Xiujun Li, Xi Yin, Chunyuan Li, Pengchuan Zhang, Xiaowei Hu, Lei Zhang, Lijuan Wang, Houdong Hu, Li Dong, Furu Wei, et al. 2020. Oscar: Object semantics aligned pre-training for vision-language tasks. In European Conference on Computer Vision, pages 121–137. Springer.

Tsung-Yi Lin, Michael Maire, Serge Belongie, James Hays, Pietro Perona, Deva Ramanan, Piotr Dollár, and C Lawrence Zitnick. 2014. Microsoft coco: Common objects in context. In European conference on computer vision, pages 740–755. Springer.

Jiasen Lu, Dhruv Batra, Devi Parikh, and Stefan Lee. 2019. Vilbert: Pretraining task-agnostic visiolinguistic representations for vision-and-language tasks. Advances in neural information processing systems, 32.

Kenneth Marino, Mohammad Rastegari, Ali Farhadi, and Roozbeh Mottaghi. 2019. Ok-vqa: A visual question answering benchmark requiring external knowledge. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 3195–3204.

Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, et al. 2021. Learning transferable visual models from natural language supervision. In International Conference on Machine Learning, pages 8748–8763. PMLR.

Colin Raffel, Noam Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei Li, and Peter J. Liu. 2020. Exploring the limits of transfer learning with a unified text-totext transformer. Journal of Machine Learning Research, 21(140):1–67.

Revanth Gangi Reddy, Xilin Rui, Manling Li, Xudong Lin, Haoyang Wen, Jaemin Cho, Lifu Huang, Mohit Bansal, Avirup Sil, Shih-Fu Chang, et al. 2021. Mumuqa: Multimedia multi-hop news question answering via cross-media knowledge extraction and grounding. arXiv preprint arXiv:2112.10728.

Shaoqing Ren, Kaiming He, Ross Girshick, and Jian Sun. 2015. Faster r-cnn: Towards real-time object detection with region proposal networks. Advances in neural information processing systems, 28.

Adam Roberts, Hyung Won Chung, Anselm Levskaya, Gaurav Mishra, James Bradbury, Daniel Andor, Sharan Narang, Brian Lester, Colin Gaffney, Afroz Mohiuddin, et al. 2022. Scaling up models and data with t5x and seqio. arXiv preprint arXiv:2203.17189.

Christoph Schuhmann, Richard Vencu, Romain Beaumont, Robert Kaczmarczyk, Clayton Mullis, Aarush Katta, Theo Coombes, Jenia Jitsev, and Aran Komatsuzaki. 2021. Laion-400m: Open dataset of clipfiltered 400 million image-text pairs. arXiv preprint arXiv:2111.02114.

Piyush Sharma, Nan Ding, Sebastian Goodman, and Radu Soricut. 2018. Conceptual captions: A cleaned, hypernymed, image alt-text dataset for automatic image captioning. In Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 2556–2565.

Noam Shazeer and Mitchell Stern. 2018. Adafactor: Adaptive learning rates with sublinear memory cost. In International Conference on Machine Learning, pages 4596–4604. PMLR.

Hrituraj Singh, Anshul Nasery, Denil Mehta, Aishwarya Agarwal, Jatin Lamba, and Balaji Vasan Srinivasan. 2021. Mimoqa: Multimodal input multimodal output question answering. In Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, pages 5317–5332.

Alon Talmor, Ori Yoran, Amnon Catav, Dan Lahav, Yizhong Wang, Akari Asai, Gabriel Ilharco, Hannaneh Hajishirzi, and Jonathan Berant. 2021. Multimodalqa: complex question answering over text, tables and images. In ICLR.

Pat Verga, Haitian Sun, Livio Baldini Soares, and William Weston Cohen. 2021. Adaptable and interpretable neural memory over symbolic knowledge. In Proceedings of NAACL-HLT, pages 3678–3691.

Zirui Wang, Jiahui Yu, Adams Wei Yu, Zihang Dai, Yulia Tsvetkov, and Yuan Cao. 2022. Simvlm: Simple visual language model pretraining with weak supervision. ICLR.

Jiahui Yu, Zirui Wang, Vijay Vasudevan, Legg Yeung, Mojtaba Seyedhosseini, and Yonghui Wu. 2022. Coca: Contrastive captioners are image-text foundation models. arXiv preprint arXiv:2205.01917.

Weizhe Yuan, Graham Neubig, and Pengfei Liu. 2021. Bartscore: Evaluating generated text as text generation. Advances in Neural Information Processing Systems, 34.

Pengchuan Zhang, Xiujun Li, Xiaowei Hu, Jianwei Yang, Lei Zhang, Lijuan Wang, Yejin Choi, and Jianfeng Gao. 2021. Vinvl: Revisiting visual representations in vision-language models. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 5579–5588.

Luowei Zhou, Hamid Palangi, Lei Zhang, Houdong Hu, Jason Corso, and Jianfeng Gao. 2020. Unified vision-language pre-training for image captioning and vqa. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 34, pages 13041– 13049.

## A Pre-training

During Pre-trainnig, we found that directly training with a mixture of all four datasets will lead to instability. We experimented with different variants and found that a scheduled pre-training can lead to a stable solution. We propose to first pretrain the model on the largest LAION dataset for 1M steps, and then continue training on the other three datasets with a fixed sample ratio. We plot the first stage of LAION training in Figure 8. We monitor the generation quality (LAION image -> text captioning), and the retrieval quality (image -> 4096 in-batch caption retrieval). As can be seen, the LAION pre-training converges after 1M steps, where we first warm up and then decrease the learning rate using a scheduler.

![](images/d94cc249d165636d34a47ec00300f5c1fe52d7aa006f980d411dcd846bd74aa1.jpg)

![](images/8409b46dc39508fa3c2d020dfd359a30067f39eb527874e43b3216853b085c7f.jpg)  
Figure 8: LAION Pre-training, validation accuracy, generation Cider score and retrieval recall score from the in-batch memory.

We further the pre-training on a mixture of the other three datasets. We plot their inference evaluation scores in Figure 9. We can see that the model is able to achieve very strong performance on these datasets, i.e. higher than 1.2 CiDEr on CC12M+3M validation set. The model also achieves strong performance on text-only reading comprehension on PAQ (similar to NQ), i.e. higher than 55% EM score. On the VQA dataset, the model is able to achieve higher than 72% VQA accuracy on the validation set. These results demonstrate the efficiency and multi-tasking capabilities of the pre-trained model. The overall retrieval accuracy from the multimodal memory consisting of captions, and passages are plotted in Figure 10, where the model is able to achieve 85% RECALL@1 from a 4K memory.

## B Model Configuration

We demonstrate the ViT configuration as follows:

```python
"vit_config": {
    "model": "ViT",
    "patches": {
    "size": [16, 16]
    },
    "hidden_size": 1024,
    "image_size": [224, 224],
    "num_heads": 16,
    "num_layers": 24,
    "mlp_dim": 4096,
    "return_pooled_output": false,
    "dropout_rate": 0.1
},
```

We demonstrate the T5-EncDec configuration as follows:

```python
"model_config": {
    "vocab_size": 32128,
    "hidden_size": 768,
    "intermediate_dim": 2048,
    "num_attention_heads": 12,
    "memory_key_dim": 768,
    "encoder_layers": 12,
    "decoder_layers": 12,
    "dropout_rate": 0.1,
    "max_distance": 128,
    "num_buckets": 32,
    "scale": 1.0,
    "retrieval_weight": 0.5,
```

![](images/449c1e640753febd4e9e4f891ce516028561bc17a32afcb02f49093c2da44f78.jpg)

![](images/b32ad2a720b748d3b52a329ea67276df89e7f931383bb71e3555a165de827964.jpg)

![](images/2e3861e2f2a843269cf30d50fad1f5ac40231e09dbf9051996c4a36d8a896dc6.jpg)

Figure 9: Mixture Pre-training, CiDEr, EM, and VQA accuracy for CC, PAQ, and VQA datasets.  
![](images/eb48e185fb621be14db44b1f725f11e4ff2b43b4c8fdc44ce3a01bc89cf069ab.jpg)  
Figure 10: Mixture Pre-training retrieval accuracy over CC, PAQ, and VQA datasets.