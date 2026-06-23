# Measuring Attribution in Natural Language Generation Models

Hannah Rashkin<sup>∗,♣♦</sup> Vitaly Nikolaev<sup>∗,♣♠</sup> Google Research Google Research

Matthew Lamm<sup>♠</sup> Lora Aroyo<sup>♠</sup> Google Research Google Research

Michael Collins<sup>♠</sup> Dipanjan Das<sup>♠♥</sup> Google Research Google Research

Slav Petrov<sup>♥</sup> Gaurav Singh Tomar<sup>♦</sup> Google Research Google Research

Iulia Turc<sup>♦</sup> David Reitter<sup>♠♥</sup> Google Research Google Research

With recent improvements in natural language generation (NLG) models for various applications, it has become imperative to have the means to identify and evaluate whether NLG output is only sharing verifiable information about the external world. In this work, we present a new evaluation framework entitled Attributable to Identified Sources (AIS) for assessing the output of natural language generation models, when such output pertains to the externa world. We first define AIS and introduce a two-stage annotation pipeline for allowing annotators to appropriately evaluate model output according to AIS guidelines. We empirically validate this approach on generation datasets spanning three tasks (two conversational QA datasets, a summarization dataset, and a table-to-text dataset) via human evaluation studies that suggest that AIS could serve as a common framework for measuring whether model-generated statements are supported by underlying sources. We release guidelines for the human evaluation studies.

## 1. Introduction

Large, pretrained neural models have advanced Natural Language Generation (NLG) performance across a variety of use cases, including text summarization, translation, and dialogue. Yet, generative neural models are known to hallucinate often, lacking faithfulness to underlying sources, for example in summarization or in grounded dialogue systems. Accurate evaluation with respect to these issues is important.

In this paper, we develop a framework for the evaluation of attribution, by which we mean the accurate use of source documents to support generated text. Attribution is closely related to issues of hallucination and faithfulness (see §2 for discussion). As a key motivating example, consider a dialog with a system that generates responses to a user’s sequence of questions:

USER: what was George Harrison’s first solo album?

SYSTEM: it was “Wonderwall Music”, released in November 1968.

USER: how old was he when it was released?

SYSTEM: he was 25 years old

If such a system, in addition to generating responses, could attribute its statements to source documents, that is, provide sufficient and concise evidence for its claims, system designers and users alike could more readily ascertain the extent to which the information it provides is supported by underlying sources. Prior work in NLG spanning diverse use cases such as summarization, dialogue response generation and data-to-text generation have investigated issues of faithfulness and “hallucination”, but have not provided a uniform and formally expressed framework to measure these errors. We discuss the relationship of our work to related work in §2.

In §3, we introduce our evaluation framework, Attributable to Identified Sources (AIS), that can be used to assess whether statements in natural language made by a system are derivable from a given underlying source. The definition of AIS (see §3.3.1) formalizes the meaning of a sentence s in context using the notion of explicatures (Carston 1988; Wilson and Sperber 2004)<sup>1</sup>, and defines attribution to some background information source P in terms of an intuitive test, asking whether “According to $P , s ^ { \prime \prime }$ . It also accommodates system outputs whose meaning is uninterpretable. AIS can be used as a pre-condition or in tandem with other metrics or evaluation frameworks to assess overall quality. For example, characteristics of the underlying source (such as “source quality”), the fluency of the generated text, and so forth, can be measured using complementary metrics that are out of scope in this work.

We propose specific instantiations of AIS for three NLG tasks (§4): response generation in a conversational QA setting (as in the example above; responses must be attributable to a provided answer document), text summarization (where the summary must be attributable to the source article), and description generation from structured tables, or table-to-text (where the description must be attributable to the source table and associated metadata). Each domain involves a number of challenges: for example, in dialogue systems a key challenge is that the meaning of system responses is highly contextually dependent.

Next, we establish the feasibility of AIS evaluations via an empirical study through conducting human evaluation experiments. We train annotators to evaluate output text from multiple models per task using task-specific instantiations of AIS. We show that in our human evaluation studies, it is possible to achieve a moderate to high degree of inter-annotator agreement (see §4 for more details). We’re also able to observe differences in model outputs’ AIS scores, following generally expected trends. As part of this work, we release the detailed guidelines for human evaluation. We believe that AIS as a framework would be essential for the evaluation of system-generated utterances across NLG tasks.

## 2. Background

Hallucations in NLG. As alluded to in §1, past work has identified the issue of hallucination in neural generation models. Wiseman, Shieber, and Rush (2017) presented challenges in data-to-text generation where neural models generate hallucinated content not supported by source data; they proposed an automatic information extractionbased metric to evaluate generated text for that particular scenario and conducted a small human evaluation study examining whether summaries are supported by source data. More recently, Parikh et al. (2020) presented a larger human evaluation study in the context of a data-to-text generation dataset entitled ToTTo, and measured hallucinations in terms of faithfulness with respect to a source data table.

Hallucination has been a salient subject of investigation in text summarization. Maynez et al. (2020) presented an extensive characterization of hallucinations, discussed behavior of models that generate content that are present in larger corpora beyond a given source and conducted a significant human study. Additional automatic QA-based methods for detecting hallucinations have been proposed by Wang, Cho, and Lewis (2020), Nan et al. (2021), among others. One of the most relevant papers, Durmus, He, and Diab (2020), involved both a human evaluation and the introduction of an automatic question–answer based evaluation method. Their human evaluation of summary sentences is similar to our two-stage annotation pipeline where they evaluate sentences in two steps — first for whether it is understandable, and second, if so, for faithfulness to the underlying source (their instructions to annotators are: “If the information conveyed by the sentence is not expressed in the source, select ‘unfaithful’.”).

In the case of response generation for dialogue, especially in scenarios that involve the system responding about the real world, research has focused on measuring the responses’ consistency to prior conversational history or their groundedness to some external evidence, that we deem to be very close to the topic of hallucination. These have been measured via dialogue-specific natural language inference methods, often via human studies and data creation (Welleck et al. 2019; Mehri and Eskenazi 2020; Gupta et al. 2021; Honovich et al. 2021; Dziri et al. 2021; Santhanam et al. 2021).

Despite a significant amount of work pertaining to hallucination spanning multiple NLG problems, there is no unified approach to evaluate whether system generated statements are supported by underlying source documents. Human evaluation studies are varied from paper to paper and detailed, reproducible annotation instructions are unavailable (Belz, Mille, and Howcroft 2020). Likewise, the use of terminology for describing and defining evaluation criteria also lacks consistency and further complicates reproducibility (Howcroft et al. 2020). General-purpose benchmarking across these tasks have gained traction (Gehrmann et al. 2021), but there has not been a standardized treatment of the attribution problem. Our paper attempts to address this gap by explicitly formalizing the evaluation of attribution as a replicable and extendable conceptual framework. As part of our definition of attribution, we outline a more formal background for “information conveyed by the text” — in particular through the use of explicatures (see Figure 1 for examples). Lastly, we demonstrate that AIS can be generalized across multiple NLG tasks in which context, source documents, and generated text can take different forms.

Fact Verification. A related field of study has dealt with the topic of fact or claim verification (Thorne et al. 2018; Thorne and Vlachos 2018; Thorne et al. 2021, inter alia). Work in this area has framed the task as retrieving supporting evidence given a claim, and optionally classifying semantic relationships between the claim and the evidence text. Modeling approaches have overlapped with recent literature examining natural language inference (Nie, Chen, and Bansal 2019). Thorne et al. (2021) have examined several human annotation tasks for the above family of problems; however, there are several key differences with this work. First, we evaluate the quality of a system generated utterance with respect to given evidence source (a fundamentally different end goal); we utilize the notion of explicatures in defining attribution; finally, we avoid absolute judgments regarding “factuality” of utterances. As mentioned in §1, rather than making factuality judgments, we deem that complementary evaluation methods such as “source quality” in tandem with AIS would be required to evaluate the factuality of utterances. As a corollary, we assume the source is a reference, and that an actual system may select sources for their trustworthiness.

Decontextualization. Choi et al. (2021) introduce the task of decontextualization, that is, the problem of taking a sentence in context and rewriting it in a way that it’s meaning is preserved, and it can be interpreted out of context. This is directly related to the idea of explicatures, which are also used in the current paper.

## 3. A Formal Definition of Attributable to Identified Sources

This section gives a formal definition of AIS, attempting to give a clear and precise definition of attribution. We first give a definition of AIS for a simple case, where the utterance from a system is a standalone proposition. In spite of the simplicity of this setting, it is highly informative, and forms the basis for the full definition of AIS. We then describe how this definition extends to a much larger set of system utterances, in particular giving a treatment of interpretability<sup>2</sup>, and contextual effects. A key idea in our model of meaning in context is the notion of explicatures (Carston 1988; Wilson and Sperber 2004; Choi et al. 2021). In a final subsection, we describe how key aspects of the AIS definition naturally lend it to operationalization, while also pointing out how certain idealizations (e.g., the notion of a “generic speaker”) must be relaxed to accommodate the practical realities of implementation.

## 3.1 An Initial Definition of AIS: Attribution of Standalone Propositions

We now give a definition of AIS for a simple but important case, where the text in question is a standalone proposition. We in general assume a setting where AIS is to be determined for a string whose meaning is ascertained relative to a context. In the following treatment we assume that time is the only non-linguistic aspect of context relevant to determining textual meaning, modeling a setting where two generic speakers communicate over a text-based channel, with no additional prior information about each other.<sup>3</sup>

We define standalone propositions as follows:

Definition 1 (Standalone Propositions)

A standalone proposition is a declarative sentence that is interpretable once a time t has been specified.

To illustrate the definition of standalone propositions, consider the following examples:

Example S1: George Harrison was 25 years old when his album ‘Wonderwall Music was released.

Example S2: He was 25 years old.

Example S3: George Harrison was 25 years old.

Example S4: George Harrison died over 15 years ago.

All four examples are declarative sentences. S1 is a standalone proposition. S4 is a standalone proposition, as it is interpretable once the time t is specified. S2 is however not a standalone proposition, as it cannot be interpreted without additional contextual information: It is unclear what “He” refers to. More subtly, S3 is also not a standalone proposition, because it lacks details of historical context.

The definition of AIS for standalone propositions is as follows:

Definition 2 (AIS for standalone propositions)

A pair (s, t) consisting of a standalone proposition s and a time t is Attributable to Identified Sources (AIS) iff the following conditions hold:

1. The system provides a set of parts P of some underlying corpus K, along with s.

2. (s, t) is attributable to P .

A pair (s, t) is attributable to a set of parts P of some underlying corpus K iff: A generic hearer will, with a chosen level of confidence, affirm the following statement: “According to $P , s ^ { \prime \prime } ,$ , where s is interpreted relative to time t.

Here, the corpus K could be a set of web pages, and the parts P could be pointers to paragraphs or sentences within K; or the corpus K could be a knowledge graph, with P as parts of the underlying knowledge graph; other examples are no doubt possible.

As an example, consider standalone proposition S1 given above, assume that the corpus K is all of Wikipedia, $t _ { 0 }$ is the present time (specifically, noon on December 21st 2021), and assume that the set P consists of a single paragraph from Wikipedia, as follows:

Example P1: George Harrison (25 February 1943 — 29 November 2001) was an English musician, singer–songwriter, and music and film producer who achieved international fame as the lead guitarist of the Beatles. His debut solo album was ‘Wonderwall Music’, released in November 1968.

Under this definition, it would be correct for a hearer to judge “(S1, t ) is attributable to P1”, because the “according to” test in the AIS definition holds. That is, it is reasonable to say according to P1, S1” where S1 is interpreted at time $t _ { 0 } { \mathrm { : } }$ “according to P1, George Harrison was 25 years old when his album ‘Wonderwall Music’ was released.”

Note that in some cases the system may provide multiple parts. The standalone proposition S may also be justified by certain forms of multi-hop reasoning (e.g., arithmetic processes) over that set of parts. The above example requires reasoning about dates and age.

AIS examples illustrating challenges in AIS judgements. These types of examples may be difficult to assess for AIS because they need extra reasoning, or assumptions about shared knowledge. These examples are purely illustrative (not from real data examples).

<table><tr><td>Evidence</td><td>Proposition Candidate</td><td>Challenges</td></tr><tr><td>George Harrison (25 February 1943 — 29 November 2001) was an English musician...His debut solo album was &#x27;Wonderwall Music&#x27;, released in November 1968.</td><td>George Harrison was 25 years old when his album &#x27;Wonderwall Music&#x27; was released.</td><td>Common sense and cultural knowledge is required to interpret the information in the proposition as it requires inferring that &quot;his&quot; is still referring to George Harrison. &quot;George&quot; is typically a male name in English; musicians release albums; therefore, &quot;his album&quot; likely refers to George Harrison, but not another unattested entity.</td></tr><tr><td>The runtime of the theatrical edition of &quot;The Fellowship of the Ring&quot; is 178 minutes, the runtime of &quot;The Two Towers&quot; is 179 minutes, and the runtime of &quot;The Return of the King&quot; is 201 minutes.</td><td>The full run-time of &quot;The Lord of the Rings&quot; trilogy is 558 minutes.</td><td>Evaluating this requires numerical reasoning, and it also requires knowing that &quot;The Lord of the Rings&quot; trilogy consists of the three films mentioned (background knowledge that may vary from person to person). Additionally, it requires assumptions that the runtime is consistently referring to the theatrical edition of these movies.</td></tr></table>

## 3.2 Extending AIS: Attribution of Sentences in Context

We now extend the previous definition of AIS to cover sentences that that go beyond standalone propositions. To do so, we will need to consider multi-sentence cases, and cases with non-empty linguistic contexts. We will also cover cases that are uninterpretable.

We first define the notion of “utterance”:

## Definition 3 (Utterance)

An utterance is a sequence of one or more sentences produced by a system or user, where a sentence may be a declarative, a question, a command, an exclamation, or a fragment. The ith system utterance is $s _ { i } = s _ { i , 1 } . . . s _ { i , \left| s _ { i } \right| } ,$ , where $s _ { i , j }$ is the jth sentence within system utterance $s _ { i } ,$ and similarly the ith user utterance is $u _ { i } = u _ { i , 1 } . . . u _ { i , | u _ { i } | }$

To briefly illustrate our approach to non-empty linguistic contexts, consider the following interaction between a user and system (originally given in the introduction; repeated here for convenience):

u : what was George Harrison’s first solo album?

$s _ { 1 } \colon$ it was “Wonderwall Music”, released in November 1968.

$u _ { 2 } \colon$ : how old was he when it was released?

s : he was 25 years old.

The system utterance $s _ { 2 } =$ he was 25 years old is clearly not a standalone proposition. As such, it cannot be evaluated for AIS given our previous definition. However, given the previous context in the interaction, intuitively the meaning of $s _ { 2 }$ is something similar to the standalone proposition “George Harrison was 25 years old when his album “Wonderwall Music” was released”. This latter “paraphrase” of $s _ { 2 } \prime _ { \mathsf { S } }$ meaning is a standalone proposition, and can be evaluated using the AIS definition for standalone propositions.

We will make this notion of “paraphrase” of the meaning of an utterance in context more formal, through the introduction of explicatures. The explicature of $s _ { 2 }$ in context of the previous utterances $u _ { 1 } , s _ { 1 } , u _ { 2 }$ is $e = G e o r g e$ Harrison was 25 years old when his album “Wonderwall Music” was released. Once explicatures have been defined in this way, they can be evaluated for AIS in exactly the same way as standalone propositions.

3.2.1 Definition of Interactions and Linguistic Context. We will use the following definition of interaction throughout the paper:

Definition 4 (Interactions)

An interaction consists of: 1) a sequence $u _ { 1 } \ldots u _ { m }$ of $m \geq 0$ user utterances; 2) a sequence $s _ { 1 } \ldots s _ { n } \cot n \geq 0$ system utterances; 3) a strict total order over the $m + n$ user and system utterances.<sup>4</sup>

This setting is intended to be quite general, including a broad class of applications where systems generate utterances. In conversational QA systems we typically have alternating user and system utterances, where $m = n ,$ , and the total ordering is $u _ { 1 } , s _ { 1 } , u _ { 2 } , s _ { 2 } , . . . u _ { n } , s _ { n }$ . In summarization tasks we have a simplified setting where $m = 0 , n = 1$ , and s<sub>1</sub> is equal to the summary generated by the system. Table-to-text tasks are similar to summarization in that $m = 0 , n = 1$ , while $s _ { 1 }$ is the description of the table generated by the system.

Each sentence has an associated linguistic context:

## Definition 5 (Linguistic Context for Sentences)

We define the linguistic context for system sentence $s _ { i , j }$ to be $c _ { i , j } ,$ where $c _ { i , j }$ is the ordered sequence of sentences (with speaker identities, user or system) that precedes $s _ { i , j }$ in the total ordering. We define the linguistic context for user sentence $u _ { i , j }$ to be $c _ { i , j } ^ { \prime } ,$ where $c ^ { \prime }$ is defined in a similar way.<sup>5</sup>

Here the definition of “sentence” is intended to be quite broad. A sentence could be a declarative sentence, a question, or a fragment (such as the string “25 years old”). Under the above definitions, the context for a user or system sentence is simply the sequence of user and system sentences that precedes it. To illustrate these definitions consider the following example:

$u _ { 1 } \colon$ what was George Harrison’s first solo album?

$s _ { 1 } .$ : it was “Wonderwall Music”, released in November 1968.

$u _ { 2 } \colon$ how old was he when it was released?

s : He was 25 years old. It was the first solo album by a member of the beatles.

Here the system utterance $s _ { 2 }$ consists of two sentences, $s _ { 2 , 1 } = H e$ was 25 years old and $s _ { 2 , 2 } = I t$ was the first solo album by a member of the Beatles.

## 3.3 Explicatures

A key goal in this section is to define AIS for sentences $s _ { i , j }$ in linguistic contexts $c _ { i , j }$ which are non-empty (i.e., which contain previous sentences in the discourse). To do this it will be critical to formalize what is meant intuitively by “the meaning of $s _ { i , j }$ in context $c _ { i , j } ^ { \prime \prime }$ . To do this we introduce explicatures (this definition is closely related to definition 1 in Choi et al. (2021)):

## Definition 6 (Explicatures)

Define the context c to be $( c _ { l } , t )$ , where $c _ { l }$ is the linguistic context and t is the time. Define c¯ to be the context $( \epsilon , t )$ where  is the linguistically empty context: that is, c¯ is a copy of c but with $c _ { l }$ replaced by . The set of explicatures $E ( c , x )$ of a sentence x in a context c is a set that satisfies the following conditions: 1) each $e \in E ( c , x )$ is a declarative sentence or question that is interpretable in context $\bar { c } ; 2 )$ each $e \in E ( c , x )$ has the same truthconditional meaning in c¯ as the meaning of sentence x in context c.

Note that the sentence x will most often in this paper be a system sentence $s _ { i , j }$ in linguistic context $c _ { i , j , }$ , but can also be a user sentence $u _ { i , j }$ in linguistic context $c _ { i , j } ^ { \prime } .$

Thus, each $e \in E ( c , x )$ is a paraphrase of x that is interpretable in the linguistically empty context and that preserves the truth-conditional meaning of x in context c. Note that $\dot { E } ( c , x )$ is a set because there may be multiple ways of paraphrasing $x ,$ which are equivalent in meaning. Given an equivalence relation between sentences that identifies whether any two sentences are equal in meaning or not, we can think of a single member of $E ( c , x )$ as a representative of the entire set $\bar { E ( c , x ) }$ . Following this, in a slight abuse of terminology we will henceforth often write “the explicature of x in context c is $e ^ { \prime \prime }$ as if there is a single unique explicature $e ,$ with the understanding that e represents the entire set $E ( c , x )$ . We will also write $E ( c , x ) = e$ as shorthand for $\bar { E } ( c , x )$ being equal to the set of all sentences whose meaning is the same as that of $e .$

In addition, we define interpretability as follows:

## Definition 7 (Interpretability)

A sentence x in context c is uninterpretable if the truth-conditional meaning of x in context c is unclear. In this case we write $E ( c , x ) = { \tt N U L L }$

Figure 1 shows several examples illustrating these definitions. Some key points are as follows:

Remark 1: In example E1, the system response is a direct answer to a question, $s _ { 2 , 1 } = 2 5$ years old. $s _ { 2 , 1 }$ itself is not a declarative sentence, but given the context (in particular the question it is answering), its explicature is the standalone proposition George Harrison was 25 years old when “Wonderwall $M u s i c ^ { \prime \prime }$ was released. This type of example — where a direct answer to a question is an entity, noun-phrase, or some other fragment, but its explicature is a standalone proposition — is important and frequent. As another example consider the following:

$u _ { 1 } \colon$ : What was George Harrison’s first solo album?

$s _ { 1 } \colon$ Wonderwall Music

```txt
Example E1
    u1: what was George Harrison's first solo album?
    s1: it was "Wonderwall Music", released in July 2006.
    u2: how old was he when it was released?
    s2: 25 years old
    E(c2,1, s2,1) = George Harrison was 25 years old when "Wonderwall Music" was released

Example E2
    u1, s1, u2 as in Example E1
    s2: he was 25 years old
    E(c2,1, s2,1) = George Harrison was 25 years old when "Wonderwall Music" was released

Example E3
    u1, s1, u2 as in Example E1
    s2: He was 25 years old. It was the first solo
    album by a member of the Beatles.
    E(c2,2, s2,2) = Wonderwall Music was the first solo album by a member of the Beatles.

Example E4
    u1, s1, u2 as in Example E1
    s2: the band was The Beatles
    E(c2,2, s2,2) = NULL

Example E5
    u1, s1, u2 as in Example E1
    s2: it was 25
    E(c2,2, s2,2) = NULL

Example E6
    u1, s1, u2 as in Example E1
    s2: He was 25 years old. Have you heard that album?
    E(c2,2, s2,2) = Have you heard the album "Wonderwall Music"?

Example E7
    u1: what was George Harrison's first solo album?
    s1: it was "Wonderwall Music", released in July 2006.
    u2: how old was he when it was released?
    E(c'2, u2) = how old was George Harrison when "Wonderwall Music" was released?

Figure 1
Examples of utterances in context, and their explicatures.
```  
$E ( c _ { 1 , 1 } , s _ { 1 , 1 } )$ = George Harrison’s first solo album em was “Wonderwall Music”

Remark 2: In Example E3, the system segment is a sequence of two declarative sentences. Each sentence has an explicature that is a standalone proposition. This type of case is again frequent and important.

Remark 3: In Example E4 the system utterance is uninterpretable, because it is not clear what “the band” is referring to. Example E5 contains disfluencies that make it difficult to reliably interpret: “it” is not the expected pronominal reference; in this context “25” becomes too ambiguous to interpret as referring to the age of a human entity.

Remark 4: Examples E6 and E7 contain questions in the system and user utterance respectively. These examples illustrate that single questions (E7) or questions within multi-sentence utterances (E6) have well-defined explicatures.

3.3.1 The Full Definition of AIS. With this background, we can now give the full definition of AIS:

Definition 8 (AIS, full definition)

A pair $( s , c ) .$ , where s is a sentence and $c = ( c _ { l } , t )$ is a pair consisting of a linguistic context and a time, is Attributable to Identified Sources (AIS) iff the following conditions hold:

1. The system provides a set of parts P of some underlying corpus $K ,$ along with s.

2. s in the context c is interpretable $( { \mathrm { i . e . , } } E ( c , s ) \neq { \mathrm { N U L L } } )$

3. The explicature $E ( c , s )$ is a standalone proposition.

4. The pair $( E ( c , s ) , t )$ is attributable to P .

The pair $( E ( c , s ) , t )$ is attributable to a set of parts P of some underlying corpus K iff: A generic hearer will, with a chosen level of confidence, affirm the following statement: “According to $P , E ( c , s ) ^ { \prime \prime }$ , where $E ( c , s )$ is interpreted relative to time t.

The definition is very similar to the earlier definition of AIS for standalone propositions, but with checks for interpretability, and with attribution applied to explicatures of system sentences. Note that AIS can only hold for system sentences that have an explicature that is a standalone proposition (condition 3). For example, the explicature in Example E6 in Figure 1 is not a standalone proposition, as it is a question. We leave the treatment of cases such as these to future work (we might for example evaluate attribution for declarative sentences within the explicature, excluding questions; or we might evaluate presuppositions within the questions themselves).

3.3.2 Attribution of Entire Utterances. In the previous sections we have described AIS for the individual sentences $s _ { i , 1 } \ldots s _ { i , | s _ { i } | }$ within a system utterance $s _ { i } .$ This assumes that such a segmentation of the utterance into sentences is available, for example, it is provided by the system. An alternative is to evaluate entire utterances $s _ { i }$ for AIS, in a “single-shot” annotation. AIS applied at the utterance level could potentially have the advantages of simplicity, and the avoidance of segmenting utterances into sentence boundaries. It has the potential disadvantage of being coarser grained, not allowing AIS judgments at the sentence level. The choice of sentence-level vs. utterance-level AIS will depend on the exact application of AIS.

It should be relatively straightforward to extend the full definition of AIS (Section 3.3.1) to apply to multi-sentence utterances. The definition of explicatures would need to be extended to multi-sentence utterances; the definition of standalone propositions would also have to be extended to apply to multiple sentences; the definition of “attributable” would also need to be extended.

## 3.4 Towards Operationalization of AIS

In the above definition of AIS, three definitions are of key importance: 1) the “according $\mathrm { { t o } ^ { \prime \prime } }$ test for standalone propositions; 2) the definition of interpretability; 3) the definition of explicatures, which are related to the interpretation of utterances in non-empty linguistic contexts. Note that it is not necessary for annotators to explicitly wield all of these definitions, or come to understand any of them in entirely formal terms, in order to provide AIS judgments. In developing human annotation guidelines for annotators who do not necessarily have background in these concepts, we relay the “according to” test and interpretability in a way that leverages natural speaker intuitions. We convey explicature through the more intuitive idea of a sentence paraphrase with respect to linguistic context. Annotators are instructed to apply the “according to” test strictly, without making further assumptions beyond what is conveyed in the text.

The formal definition of AIS makes several idealizing assumptions that must be relaxed in practical settings. In lieu of the posited “generic hearer”, the judgments of actual annotators will naturally be influenced by the particulars of their interpretive capacities, stemming from differences, for example, in cultural background and domain expertise. Table 1 lists several instances where such differences could conceivably affect judgments. These effects are, to some extent, inherent to implementing AIS using human judgments.

## 4. Human Evaluation Study

We evaluate the feasibility of human AIS assessment for three NLG tasks: conversational question answering, summarization, and table-to-text generation. To quantify the significance of human judgements, we present evaluators with the output of different models for each of the tasks.

The set-up for these annotation tasks is to ask annotators to rate the AIS quality of s, some model produced output given some attributed source P . In the conversational QA and summarization settings, P is a document or passage from a document, while in the table-to-text setting P is a table and its description. For conversational QA, annotators are also provided with a context c, which is the set of previous conversation turns. c is used to help annotators understand the contextualized meaning of the model output, what we formally define as explicature in §3.3.

Because this is a challenging task with many possible edge cases (such as those discussed in Table 1), we ask five annotators to judge each example. In our results section, we compare to the consensus answer (if there is one) for simplicity. In future work, researchers who wish to use AIS for evaluating systems might find use in distinguishing between cases that are more clear cut (i.e., unanimous) versus those where there may be some inherent ambiguity.

## 4.1 Task Design

We break the annotation task into two stages described in §4.1.1 and §4.1.2, which mirrors the formal steps in the AIS definition (§3.3.1) First, the annotators are asked if they are able to understand and identify the information being shared in the model output without seeing the source document (i.e., whether it is interpretable on its own). Then, if the output is deemed interpretable, the annotators are shown the “attributed source” P and asked whether all of the information that is shared in S can be attributed to P (i.e., whether it is AIS). As described in the results sections, the splitting of the task into these two steps helps annotators to first filter out outputs that are badly formed (e.g., ungrammatical to the point of impeded intelligibility) or too ambiguous (e.g., unclear pronouns) to appropriately evaluate the attribution. In the results, we report scores based on the annotator consensus (i.e., majority vote): the percent of total examples marked as interpretable (Int in Tables) and the percent of interpretable examples that were marked as AIS (AIS). In some datasets, certain examples were flagged as difficult to annotate due to legibility-related issues (see §4.1.3). For those cases, we separately report the percentage of examples that were flagged (Flag) and thus excluded from the interpretability and AIS scores.

4.1.1 Interpretability Rating. In the initial stage of the annotation task, we show the annotators the model output s and any preceding context c without showing the source. We ask them to identify the interpretability by posing a yes/no question. For example, in the summarization task the annotators are asked:

Is all of the information relayed by the system summary interpretable to you?

Note that context c is populated with preceding turns of the system–user interaction<sup>6</sup> in the conversational QA task, whereas in summarization and table-to-text tasks it is always empty. In the instructions, the context c is explicitly called out to be used in interpreting output s in the conversational QA task.

Here, the goal is to tease out if the model-generated output s contains any potential ambiguity that would prevent or misguide establishing attribution to its source P . Anaphora resolution is the main source of this type of ambiguity, where deictic elements do not have clear antecedents within s or its context — for example, pronominal usage with an unclear or broken coreference chain or definite noun phrases as first mentions. Additionally, syntactic ambiguity or disfluency may also result in diminished interpretability of s (see Examples E4, E5 in Figure 1).

We acknowledge potential anthropomorphizing effects on how annotators interpret the system output (Gopnik and Wellman 1992). Because cooperative meaning co-construction between interlocutors is the default communicative strategy of interhuman interaction (Grice 1975), when faced with ambiguities and slight discrepancies in the system output, annotators may be “forgiving” of diminished interpretability, especially if the underlying source is present and can help recover missing context.

In our experiments we have found that not presenting the source at this stage is crucial for ensuring that evaluators are strict in their assessment of interpretability of the system output (see Figures 1, 1, and 1 for how it was implemented in the task interface).

4.1.2 AIS Rating. If an annotator selects “yes” for the interpretability question, we show them the source P and ask them whether all of the information relayed in the output s can be supported by P . For example, in the conversational QA task the annotators are asked:

Is all of the information provided by the system response fully supported by the source document?

Note that the P for the conversational QA task is the retrieved document that serves as the source of the system output s. In the summarization task P is the original news article from which the summary in s was derived. In the table-to-text task P is the original table, highlighted cells, and table metadata (table title, section title, and section text) from which the textual table description is generated.

In the instructions, we tell annotators to first think about all of the information that is contained the output including: what’s directly stated in the output sentence verbatim as well as any explicatures that can be made from the output with respect to the context, such as inferring pronoun references from the conversational history.

Annotators are instructed to only mark output as attributable if it is clear that all parts can be directly inferred from the source. The instructions specifically call out to utilize the paraphrase test:

In determining this question, ask yourself whether it is accurate to say “the provided news article says. . . ” or “according to the news article. . . ” with the system summary following this phrase.

If the output is misrepresenting information from the source because it is misleadingly worded, missing important context, or even changing only slight details, these cases are all counted as “not fully attributable”.

4.1.3 Flag Rating. A special rating is reserved for flagging items that would be disqualified from the the task altogether because they flout the range of possible relationships between the utterance, its context, and the source defined in 3.3.1.

In practical terms, these are tasks that are too malformed for annotators to perform judgements on. This category includes tasks with rendering issues in the interface (missing task elements, e.g., empty utterance), corrupted text resulting in non-communicative utterances (bad text encoding, HTML artifacts), underspecified source (the source document itself is ambiguous because it is too short and may contain unresolved reference chains), or a source that is difficult to understand because it requires expert-level knowledge.

Once a task is flagged, it is disqualified from the rating queue of the annotator who flagged it. Other annotators may choose not to flag this item; cumulative ratings and interannotator agreements are calculated for all non-flagged ratings of a task (see the flag sections in the annotator guidelines for conversational QA, summarization, and table-to-text) Section 7.

4.1.4 Limitations. By asking yes/no questions, we can greatly reduce the complexity of this task for annotators. However, for some applications of AIS measures, it may be useful to have more fine-grained measures. Additionally, we ask annotators to evaluate the entire output (rather than sentences or specific spans) under the reasoning that if even one span within the model output is not AIS, then the whole output is not AIS (cf. Maynez et al. (2020), Durmus, He, and Diab (2020)).

We also acknowledge that there are other aspects of model output quality (e.g., relevance, non-redundancy, etc.) not evaluated here. We focus on the separate evaluation of AIS as part of a focused effort towards quantifying the attribution itself, disentangled from other desirable generation qualities.

## 4.2 Human Evaluation Procedure

The ratings were performed by a group of nine paid full-time annotators under the guidance and supervision of a project manager. The annotator team is based in Hyderabad, India; the annotators are native speakers of the Indian dialect of the English language. The annotators do not have a background in linguistics. They were trained for this specific task.

Three separate user interfaces were developed for performing the evaluation in this study: one for the conversational QA tasks evaluating the output of models trained on QReCC and WoW datasets, another for summarization tasks evaluating the output of models trained on the CNN/DM dataset and lastly one for table-to-text tasks evaluating the output of models trained on the ToTTo dataset. The interfaces share many fundamental design elements with task dependent modifications. For example, the conversation QA interface contains a devoted element for displaying the conversational history. All three interfaces explicitly hide the source document/table at the stage when interpretability of the system output is evaluated (see the Appendix for the interface layouts and annotator prompts (Figures 1, 2, 1, 2, 1, and 2).

The annotators were trained on the tasks in a series of stages. First, a pilot study of 50–100 items was conducted with the first iteration of the annotator instructions. As part of the pilot, all ratings were required to have written justifications elaborating the reasoning for the provided rating. The results of the pilot were analyzed by the authors to identify common errors patterns; collected justifications were helpful in understanding the reasoning annotators used to arrive at their ratings. The results of the review were communicated back to the annotators, and the instructions were modified to emphasize areas leading to common ratings errors.

Next, a portion of the ratings was inspected by the authors for persistent error patterns and the feedback communicated to annotators. Additionally, the annotators collected edge cases where they found it difficult to make judgements. These edge cases were adjudicated by the authors; recurring complex patterns were used to expand the annotator guidelines (see the Appendix for full final instructions for conversational QA, summarization, and table-to-text).

Finally, the annotator team performed internal audits on a subset of completed tasks.

Annotators were initially trained on the conversational QA tasks; other tasks and training were introduced subsequently.

## 5. Experiments

In the following section, we demonstrate the utility of the AIS templates by showing how it can be applied to three different tasks (conversational QA, summarization, and table-to-text generation) in which the model output is — by design — always meant to be attributable to some source document. We instantiated the AIS annotation template for four datasets in these domains (see Table 2) and performed human evaluation studies on generated outputs from multiple models. In order to show the applicability of AIS in detecting nuanced differences between different types of model outputs, we specifically chose models for each dataset that would represent a range of different types of outputs rather than just selecting a set of state-of-the-art models. We also annotated a selection of gold references from each dataset to better understand the AIS quality of existing datasets in these areas. We end with analysis of how effectively humans can annotate AIS as well as a discussion of various interpretability and AIS patterns that we found in the resulting annotations.

## 5.1 QReCC Answer Generation

Set-up. We use the QReCC dataset (Anantha et al. 2021), a collection of multi-turn conversational QA interactions that extends conversations coming from NaturalQuestions (Kwiatkowski et al. 2019), QUAC (Choi et al. 2018), and CAST-19 (Dalton et al. 2020). In this task, a model is given a conversational history and generates a contextualized response. We use a task set-up where the document passage containing the answer to the current query has already been retrieved (using the oracle retrieved document passage as the attributed source). We use different variations of T5 models including both base and small size variants. First, we use the pre-trained T5 models (PT) by themselves by prompting the model (formatted as: “Query:... Conversation History: ... Document: ... Answer:”). We also use a version of T5 that has been fine-tuned on QReCC (FT) which uses special tokens to separate the query, context, and document instead of natural-language prompts. Lastly, to sanity-check the AIS measures, we use a version of the model (no evidence) that only sees the query and conversation history but not the document at generation time. We expect that the AIS subscores should be much lower in the model that does not use the evidence from document to generate the answer.

Table 2  
Summary of tasks used in human annotation study.

<table><tr><td>Task</td><td>Dataset</td><td>C</td><td>P</td><td>S</td></tr><tr><td>Conversational QA</td><td>QReCC (Anantha et al. 2021)</td><td>Conversational History</td><td>Retrieved Document</td><td>Response</td></tr><tr><td>Conversational QA</td><td>Wizard of Wikipedia (Dinan et al. 2019)</td><td>Conversational History</td><td>Retrieved Fact</td><td>Response</td></tr><tr><td>Summarization</td><td>CNN/DM (Nallapati et al. 2016)</td><td>N/A</td><td>Source Article</td><td>Summary</td></tr><tr><td>Table-To-Text</td><td>ToTTo (Parikh et al. 2020)</td><td>N/A</td><td>Table, Table Description</td><td>Caption</td></tr></table>

Results of human study on 200 examples from QReCC test set (randomly sampled from set of examples where conversation length ≤ 5 turns). PT= pretrained model, FT=fine-tuned on QReCC training data.

<table><tr><td>Model</td><td>Size</td><td>Int</td><td>AIS</td></tr><tr><td rowspan="2">T5-PT (with Evidence)</td><td>Small</td><td>43.0*</td><td>82.6</td></tr><tr><td>Base</td><td>47.0*</td><td>69.1*</td></tr><tr><td rowspan="2">T5-FT (no Evidence)</td><td>Small</td><td>57.8*</td><td>25.2*</td></tr><tr><td>Base</td><td>59.8*</td><td>21.8*</td></tr><tr><td rowspan="2">T5-FT (with Evidence)</td><td>Small</td><td>99.0</td><td>87.9</td></tr><tr><td>Base</td><td>98.0</td><td>87.2</td></tr><tr><td colspan="2">Reference</td><td>99.0</td><td>87.8</td></tr></table>

\* Indicates that the result is significantly lower than the highest score in the column (with p < 0.01).

Results. We show results in Table 3. The model outputs’ interpretability increases substantially after fine-tuning (by about 50 points). The AIS subscore is highest in the finetuned model that uses evidence in its input. As expected, the AIS is drastically lower in the model that does not use the document as input at generation time (the no evidence model) which is both interpretable and AIS only 15% of the time. Differences between model sizes (small vs. base) are generally not significant except for the pretrained-only model, though the AIS scores of the smaller versions are typically slightly higher.

Results of human study on 200 examples from Wizard of Wikipedia test set (Dinan et al. 2019) (the seen topic split, using only conversation turns where the previous turn has a question mark).

<table><tr><td>Model</td><td>Flag</td><td>Int</td><td>AIS</td></tr><tr><td>WoW Baseline (Dinan et al. 2019)</td><td>4.0</td><td>84.4*</td><td>19.8*</td></tr><tr><td>Dodeca (Shuster et al. 2020)</td><td>8.5</td><td>100.0</td><td>60.1*</td></tr><tr><td>T5 (Raffel et al. 2020)</td><td>5.5</td><td>98.4</td><td>39.8*</td></tr><tr><td>T5 (with Controls) (Rashkin et al. 2021)</td><td>7.5</td><td>99.5</td><td>92.4</td></tr><tr><td>Reference</td><td>4.0</td><td>100.0</td><td>15.6*</td></tr></table>

\* Indicates that the result is significantly lower than the highest score in the column (with p < 0.01).

## 5.2 WoW Answer Generation

Set-up. We used the seen portion of the test set from Wizard of Wikipedia (Dinan et al. 2019). In this task, a model is given a conversational history and generates a contextualized response based on information from Wikipedia. As with QReCC, we again use a set-up where the Wikipedia sentence has already been retrieved (using the oracle retrieved sentence as the attributed source). To avoid chit–chat style utterances that may not be sharing new information, we sampled 200 examples per model where the previous utterance was a question (contains ‘?’). We used the models from Rashkin et al. (2021). That paper introduced a controlled T5 model trained on the Wizard of Wikipedia data which uses control tags and re-sampling to target generations that are more faithful to the document (by looking at heuristics such as entailment metrics, lexical precision, and first-person usage). Similar to that paper, we also compared with three models that are seq2seq-style conversation models: the original answer generation system from Dinan et al. (2019), the Dodecadialogue multitask system from Shuster et al. (2020) and a T5-base model (Raffel et al. 2020) finetuned on Wizard of Wikipedia data. Because the model from Rashkin et al. (2021) was specifically trained to be more faithful to evidence, we expect that it will score higher in the AIS category.

Results. We show results in Table 4. Compared to the QReCC data (in which only a few examples were flagged), more examples were flagged with the Wizard of Wikipedia data, which we included as an extra column. The general trend of results is similar to what was found in the human evaluations of faithfulness and subjectivity in Rashkin et al. (2021). As expected, the model that has specific controllable inputs for increasing the model’s faithfulness to the input document achieves the highest the AIS scores overall. We also note that the AIS scores of the gold references is lower than the model outputs. We discuss this more in Section 5.5.5.

## 5.3 CNN/DM Summarization

Set-up. We extend our evaluation framework for a second task, summarization to confirm that AIS can be more broadly applicable. AIS is crucial in summarization where a generated summary (S) must be well-supported by the source article (P ). In contrast to some of the prior work in hallucination evaluation in summarization (Durmus, He, and Diab 2020; Maynez et al. 2020), the annotators in our task evaluate the full summary for attribution (rather than at a sentence-level or a span-level), in order to account for cases where two individual text spans may be attributable to a source document but — when composed together — convey information that is different from the source document (e.g., misordered events, pronouns that no longer have the correct references when misordered, etc.). As a first step in applying AIS to summarization, we compare the performance of three different approaches (abstractive vs. extractive vs. hybrid) on 200 examples randomly sampled from the CNN/DM (Nallapati et al. 2016) test set. The source articles in this dataset come from articles in CNN and DailyMail news and the summaries are extracted from bulleted highlights that were included with the article by the journalists. We expect that high-quality AIS annotations will show a trend where extractive systems achieve higher AIS scores because they are copying directly from the source without adding anything. First, we used MatchSum (Zhong et al. 2020), a state-of-the-art extractive summarization model. Because this model is extractive, it is expected that it will be the least prone to hallucinations. We also used an abstractive summarization system, BigBird (Zaheer et al. 2020). Lastly, we used Pointergenerator Networks from See, Liu, and Manning (2017) — a hybrid approach that is uses an abstractive seq2seq model but with an explicit copy mechanism that can extract information from the source document.

Table 5  
Results of human study on 200 examples from CNN/DM test set (randomly sampled). Of the three models we tested with, unsurprisingly the more extractive models have higher AIS scores.

<table><tr><td>Model</td><td>Approach</td><td>Int</td><td>AIS</td></tr><tr><td>MatchSum (Zhong et al. 2020)</td><td>Extractive</td><td>90.0</td><td>99.4</td></tr><tr><td>Pointer-Gen (See, Liu, and Manning 2017)</td><td>Hybrid</td><td>90.0</td><td>97.8</td></tr><tr><td>BigBird (Zaheer et al. 2020)</td><td>Abstractive</td><td>90.0</td><td>87.2*</td></tr><tr><td>Reference</td><td>-</td><td>86.0</td><td>54.1*</td></tr></table>

\* Indicates that the result is significantly lower than the highest score in the column (with $p < 0 . 0 1 )$

Results. We show results in Table 5. The more extractive approaches generally reach higher AIS subscores. This is a somewhat expected result — extractive systems are less likely to output hallucinations as they are quoting information verbatim from the documents. As with Wizard of Wikipedia, the AIS scores of the gold reference summaries is surprisingly lower than the model output, which we will discuss more in Section 5.5.5.

## 5.4 Table-to-Text ToTTo data

Set-up. Lastly, we show the utility of extending AIS to a table-to-text task where P is a table rather than a text document. S is a sentence generated by a model to describe some highlighted portion of the table. We chose the ToTTo dataset (Parikh et al. 2020), testing with T5 and ByT5 models that were previously used with this data in the GEM benchmark (Gehrmann et al. 2021). We experiment with two different sizes of ByT5 and three different sizes of the T5 architecture. As before, we sampled the output of 200 examples from the test set. We also annotated 200 ground-truth references from

## Table 6

Results of human study on 200 examples from ToTTo test set (model output) and development set (ground-truth references).

<table><tr><td>Model</td><td>Flag</td><td>Int</td><td>AIS</td></tr><tr><td>ByT5-Base</td><td>0.0</td><td>78.9*</td><td>88.5</td></tr><tr><td>ByT5-XL</td><td>0.0</td><td>79.5*</td><td>86.2</td></tr><tr><td>T5-Small</td><td>3.0</td><td>86.5</td><td>88.6</td></tr><tr><td>T5-Base</td><td>5.0</td><td>91.1</td><td>86.6</td></tr><tr><td>T5-XL</td><td>6.0</td><td>89.4</td><td>85.1*</td></tr><tr><td>Reference</td><td>0.0</td><td>83.9</td><td>91.0</td></tr></table>

\* Indicates that the result is significantly lower than the highest score in the column (with p < 0.01)

## Table 7

Annotator agreement measured as interannotator agreement (left half of the table) or as agreement with expert consensus (right half of the table, only measured on QRECC and CNN/DM tasks). Metrics include — F1: a F1 measure comparing individual ratings to the consensus rating; PA: pairwise agreement as percentage of individual pairs that agree; α: Krippendorff’s alpha measure comparing pairs of individual ratings.

<table><tr><td rowspan="2">Task</td><td colspan="6">IAA</td><td colspan="6">vs. Expert</td></tr><tr><td>F1</td><td>Int PA</td><td> $\alpha$ </td><td>F1</td><td>AIS PA</td><td> $\alpha$ </td><td>F1</td><td>Int PA</td><td> $\alpha$ </td><td>F1</td><td>AIS PA</td><td> $\alpha$ </td></tr><tr><td>CNN/DM</td><td>.83</td><td>.80</td><td>.46</td><td>.92</td><td>.89</td><td>.69</td><td>.48</td><td>.60</td><td>-.04</td><td>.81</td><td>.86</td><td>.61</td></tr><tr><td>QReCC</td><td>.97</td><td>.96</td><td>.91</td><td>.93</td><td>.89</td><td>.76</td><td>.77</td><td>.81</td><td>.54</td><td>.77</td><td>.78</td><td>.54</td></tr><tr><td>WoW</td><td>.88</td><td>.93</td><td>.60</td><td>.95</td><td>.88</td><td>.79</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>ToTTo</td><td>.95</td><td>.95</td><td>.84</td><td>.92</td><td>.92</td><td>.74</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr></table>

examples in the dev. set (as the test set does not have gold-truth references publicly available).

Results. We show results in Table 6. The model with the most “interpretable” responses was T5-base, with the ByT5 architectures being significantly less interpretable. On the other hand, the T5 architecture responses were more likely to be flagged (according to the annotators this was because the flagged responses contained artefacts like unintelligible character encoding errors). Generally, we don’t observe statistically significant differences in the AIS subscores though the larger architectures tended to have slightly lower AIS scores (similar to our observations of Table 3).

## 5.5 Annotation Quality

In this section we discuss the further implications of the human annotation results. We focus on two primary questions: (1) can humans reliably annotate AIS? and (2) what do our measured AIS ratings indicate about NLP data and models?

Quality measure on samples of annotations for conversational QA, summarization, and table-to-text tasks. Snapshots represent consecutive annotation sprints with individual annotator judgements (Ann) replicated at 5 per task. A sample (Smpl) of each snapshot was evaluated by a project lead on the annotator team. The quality of annotations (Qual) was assessed over a varying number of snapshots for each task. The evaluated annotations exclude flagged tasks.

<table><tr><td rowspan="2">Snapshot</td><td colspan="3">Conversational QA</td><td colspan="3">Summarization</td><td colspan="3">Table-to-Text</td></tr><tr><td>Ann</td><td>Smpl</td><td>Qual</td><td>Ann</td><td>Smpl</td><td>Qual</td><td>Ann</td><td>Smpl</td><td>Qual</td></tr><tr><td>1</td><td>642</td><td>.04</td><td>1.00</td><td>88</td><td>.06</td><td>.67</td><td>261</td><td>.08</td><td>1.00</td></tr><tr><td>2</td><td>726</td><td>.05</td><td>1.00</td><td>339</td><td>.06</td><td>.87</td><td>2,518</td><td>.19</td><td>.96</td></tr><tr><td>3</td><td>1,895</td><td>.03</td><td>1.00</td><td>469</td><td>.10</td><td>.94</td><td>2,463</td><td>.30</td><td>.97</td></tr><tr><td>4</td><td>2,520</td><td>.04</td><td>.97</td><td>682</td><td>.08</td><td>1.00</td><td>1,151</td><td>.34</td><td>.96</td></tr><tr><td>5</td><td>-</td><td>-</td><td>-</td><td>608</td><td>.08</td><td>1.00</td><td>849</td><td>.30</td><td>.94</td></tr><tr><td>6</td><td>-</td><td>-</td><td>-</td><td>652</td><td>.08</td><td>1.00</td><td>-</td><td>-</td><td>-</td></tr><tr><td>7</td><td>-</td><td>-</td><td>-</td><td>928</td><td>.03</td><td>1.00</td><td>-</td><td>-</td><td>-</td></tr><tr><td>Total</td><td>5,783</td><td>.04</td><td>.99</td><td>3,766</td><td>.07</td><td>.98</td><td>7,242</td><td>.26</td><td>.96</td></tr></table>

5.5.1 Interannotator Agreement. We show the interannotator agreement (IAA) for crowd annotators in the left half of Table 7. The metrics we used include Krippendorff’s alpha comparing individual ratings, pairwise agreement (PA) comparing individual ratings and an F1 score comparing individual ratings to the consensus (majority vote). Agreement results are generally moderate to high, displaying that — while this is a challenging task — the annotators are able to be fairly consistent with one another. The alpha scores are generally lowest on the summarization CNN/DM task, perhaps because the output text is much longer in summarization, increasing the complexity of the rating task. The F1 scores are similarly high, particularly on the AIS ratings.

5.5.2 Audits. Separately, the annotator team also performed internal audits on the annotation quality where a project lead from the annotator team examined a sample of individual annotator judgements at different points (snapshots) of the annotation process (Table 8). QRECC and WoW annotations were evaluated together as the broader conversational QA annotation task. The overall reported quality is in the high nineties for all three tasks with slight variations. The annotation quality for the conversational QA tasks remains high across all snapshots; we attribute this to the annotators extended experience with the task prior to the annotation of this dataset<sup>7</sup>. The quality of the summarization annotations shows an increase over snapshots, as annotators internalize the guidelines and gain expertise in the task. The quality of the table-to-text annotations fluctuates and is generally the lowest of the three tasks; we attribute this to a much larger sample for which quality was measured. Overall, across the three tasks, the larger the quality evaluated sample, the lower the overall reported quality. Barring genuine task differences that would lead to variations in annotation quality, this suggests that the reported table-to-text quality of annotations is the most representative of all three tasks.

## Table 9

Average completion times (ACT) for ratings tasks in seconds. Conversational QA tasks include evaluation of generated text for QReCC and WoW. Summraziation tasks include evaluation of generated text for CNN/DM. Table-to-text tasks include evaluation of generated text for ToTTo. Justifications were required for all question tasks at the pilot stage, but not at the production stages. Average completion times decrease for all three task types as annotators gain more experiences over the amount of observed tasks (Tasks), but are always relatively longer for summarization. Note that the average completion times may be reduced further for summarization with more tasks observed by annotators, a pattern we see in the conversational QA and table-to-text task types.

<table><tr><td rowspan="2">Stage</td><td rowspan="2">Justification</td><td colspan="2">Conversational QA</td><td colspan="2">Summarization</td><td colspan="2">Table-to-Text</td></tr><tr><td>Tasks</td><td>ACT, secs.</td><td>Tasks</td><td>ACT, secs.</td><td>Tasks</td><td>ACT, secs.</td></tr><tr><td>Pilot</td><td>+</td><td>75</td><td>375.30</td><td>50</td><td>687.02</td><td>100</td><td>324.72</td></tr><tr><td>Start</td><td>-</td><td>762</td><td>136.76</td><td>187</td><td>308.14</td><td>136</td><td>238.40</td></tr><tr><td>Finish</td><td>-</td><td>4,022</td><td>73.19</td><td>900</td><td>263.55</td><td>1,496</td><td>193.95</td></tr></table>

5.5.3 Crowd Annotator Performance. We also observe average task completion times decrease across all types of tasks as the annotators are exposed to more tasks and internalize the instructions (Table 9). Initial pilots for the conversational QA, summarization, and table-to-text tasks included required rating justifications for interpretability and AIS questions as part of annotator training. Once the production annotation started and the justifications were no longer required, completion times decreased significantly for all types of tasks, which we attribute primarily to the annotators no longer typing out detailed justifications of their ratings, but also overall internalization of the guidelines. The effects of annotators internalizing the guidelines are also evident when comparing completion times at production annotation start and finish: average task completion times decrease for all three types of tasks as annotators are exposed to more tasks and gain more experience.

At the same time, the absolute task completion times are consistently and substantially different across the three tasks suggesting their uneven complexity, with conversational QA taking the shortest amount of time to complete, summarization requiring the longest, and table-to-text falling in-between. This pattern follows the trend in the distribution of inter-annotator agreement across the three tasks: tasks with shorter completion times generally have higher interannotator agreement. We postulate that this is primarily due to the difference in the amount of context that is necessary to perform ratings. Although conversational QA tasks may contain several turns of preceding interactions between the system and the user as well as the source document, the amount of information in the source articles in the summarization task is substantially larger. Likewise, source tables in the table-to-text task can be extensive and have the added information complexity of cell highlighting and table metadata. Finally, register and discourse structure effects may be at play here as well. Conversational QA tasks build upon colloquial interactions between the user and the system, setting up the context of the interaction in shorter utterances and helping annotators anticipate the contents of the source document. Likewise, Wikipedia, news articles, and tables package information differently as they serve somewhat different communicative goals, and it is possible that one of these source types is more amenable to inspection required for performing AIS ratings.

<table><tr><td>Table 10Selected conversational QA examples marked as AIS by annotators but not AIS by experts where differences in how entities are named (first name vs. last name) in the response vs. document may cause some ambiguity as to whether the document is accurately describing the same person. Some people may also have background knowledge about the entities involved that helps them disambiguate whether these documents are referring to the same “mayer” or “adams” as the question.</td></tr><tr><td>Example 1Querywhat is a charity john mayer works for?Responsein 2002, john mayer created the back to you fund, a nonprofit organization that focuses on fundraising in the areas of health care, education, the arts and talent development.Attributed Documentpersonal life on his third episode of current mood , mayer revealed he had been sober for two years. he stopped drinking after having what he says was a six-day hangover after drake ’s 30th birthday party. relationships mayer has never married, but has been romantically involved with jennifer love hewitt , jessica simpson , minka kelly , jennifer aniston , and katy perry . philanthropy in 2002, mayer created the “back to you” fund, a nonprofit organization that focuses on fundraising in the areas of health care, education, the arts and talent development. the foundation auctions exclusive john mayer items, such as guitar picks, t-shirts and signed cds. ...</td></tr><tr><td>Example 2Conversation HistoryUSER: where did john adams practice law?SYSTEM: harvardQuerywhat happened after john adams practiced law at harvard?Responsein 1756, john adams began reading law under james putnam, a leading lawyer in worcester.Attributed Documentlaw practice and marriage abigail smith adams – 1766 portrait by benjamin blyth john adams – 1766 portrait also by blyth in 1756, adams began reading law under james putnam, a leading lawyer in worcester. in 1758, he earned an a.m. from harvard, and was soon admitted to the bar, having completed his studies under putnam. he developed an early habit of writing about events and impressions of men in his diary; this included james otis jr. ’s 1761 legal argument challenging the legality of british writs of assistance , allowing the british to search a home without notice or reason. ...</td></tr></table>

5.5.4 Expert Ratings. Where AIS is used as a metric for ranking generative models, the internal consistency of crowd annotations is paramount. But, to help illuminate the inherent challenges in calibrating this annotation task, we also compare the crowd ratings with those of expert on a small set of examples. Due to the challenges of scaling expert evaluations, we limited expert ratings to two tasks (CNN/DM and QReCC) with 50 examples each. The experts (two co-authors) first annotated the examples separately from each other using the same interface as the crowd annotators and then discussed their answers to reach a consensus. Expertise here might be derived from general educational background (a different approach to close reading), the ability to discuss annotations (and to do so carefully at self-guided pace), specialized knowledge, and first-hand familiarity with the evaluation framework. Expertise does not imply that the experts have more experience performing the task than the crowd annotators.

<table><tr><td>Table 11Selected summary examples marked as interpretable by annotators but non-interpretable by experts. We note that the style of language in these summaries can be vague which may increase the difficulty in leaving a binary interpretability judgement.</td></tr><tr><td>Example 1Summarydeciding who you will vote for may have more to do with your family than who won the leaders debate ( above ) finds study which looked at the voting habits of twins born in the uk .the aim was to explore how much nature and nurture influence our party political allegiances and potential voting preferences</td></tr><tr><td>Example 2SummaryCharlie Stayt was broadcasting live from a primary school in Southampton .He missed out the letter ‘c’ when he scrawled the word on a whiteboard .Outraged viewers took to Twitter to complain about the spelling error .Stayt later described the gaffe as ’one of those things’</td></tr><tr><td>Example 3Summaryuniversity lecturer dr alex russell shares his expert advice .dr russell says that anyone can improve their tasting skills in four hours .</td></tr><tr><td>Example 4Summaryin fact , it ’s an advert from cosmetics giant revlon for their latest lipstick .the stylish ad is filmed entirely in black and white , with just a slick of pink visible on the woman’s lips.revlon uk ’s new global tag line , love is on , is the label ’s first major relaunch in more than a decade .</td></tr></table>

In order to account for natural ambiguity in assigning a rating category, experts marked some cases as “either option acceptable”. We compare the individual crowd annotator ratings to the expert consensus in the right half of Table 7. Crowd annotators tend to agree with each other more than they agree with experts, which is expected due to differences in background, incentives, and procedure, although there is still reasonably consistent agreement in most cases. On closer inspection, we find that most disagreements are cases where there is underlying ambiguity caused by vagueness in the evidence or model output. In these cases experts erred more on the side of being critical of the model and crowd annotators erred more towards being lenient. In the case of conversational QA, most of the AIS disagreements involved cases where the document and the response do not refer to an entity using the same naming conventions (e.g., using both first and last name; see Table 10) leaving some ambiguity that the document is referring to the same entity as the response. The greatest source of disagreements overall is the interpretability question in the summarization task (see examples in Table 11). The summaries in the CNN/DM dataset were originally crawled from high-level article highlights, and experts observed that — due to the linguistic style of these highlights — there were many cases where the language may be vague or ambiguous, making this dimension more challenging. Because we use interpretability as a pre-filtering stage for the AIS question, we make allowances for the annotators being more inclusive. Despite the differences on the interpretability dimension, they generally agreed with experts on most AIS questions, our primary evaluation dimension.

5.5.5 Limitations of Gold References. The last rows in Tables 3, 4, 5 and 6 show annotation results on reference answers sampled from these datasets. The results demonstrate that there is actually a limit on the AIS quality of the data itself in multiple tasks. We include examples of non-AIS references in Table 12 to illustrate what some of these examples look like. We hypothesize that this is because the originators of the data were not specifically instructed to be as faithful to the underlying documents as possible. In the case of Wizard of Wikipedia (Dinan et al. 2019), the gold response is only AIS 16% of the time. But, this dataset was constructed for a different objective — to contain both informative and engaging responses. The MTurk workers who created the data were provided documents to enhance their conversations but could do so at their own discretion, often including their own thoughts and opinions in the conversation as well. This is also reflected in the CNN/DM AIS scores — summaries in CNN/DM are only attributable to the documents in 54% of the interpretable examples. Looking more closely, we speculate that this may be due to the post-hoc data creation process used to extract summaries from article highlights written by journalists. We observed that the reference summaries in CNN/DM may sometimes refer to external pieces of information that may have accompanied the article (a picture, a headline, etc.) or sometimes make assumptions about what the intended audience of the article might already know that can affect either the interpretability or AIS scores (see Example 1 in Table 12 and Example 3 in Table 1). These results indicate that there is still a need for high-quality AIS data for training new NLG models.

5.5.6 Examples. In the Appendix, we separately list textual examples rated as uninterpretable (Table 1), interpretable but not AIS (Table 2), or both interpretable and AIS (Table 3). For the table-to-text task, we present examples in a more visual figure, Figure 1, for better legibility. Common factors in marking text as “uninterpretable” include repetitive, degenerate language and ambiguous pronouns and ellipses. Additionally, some outputs are marked as uninterpretable because they are hard to understand “on their own”. Whether or not a piece of text can be understood may also rely on things like commonsense and background knowledge that could vary depending on annotators backgrounds (see Example 3 from Table 1). Ambiguous references can also affect both interpretability and the AIS scores. In Example 2 of Table 2, the retrieved document did not provide enough information to completely verify the response since it never refers to Ann Veneman by her full name. This is a seemingly minor detail, but annotators were often sensitive to this type of example since they could not verify whether the document was actually referring to the same entity as the model output. Another type of non-AIS output that frequently appeared in the QReCC data were cases where a model outputted a seemingly informative statement that — instead of being grounded to the document — was actually grounded to a previous conversation turn, sometimes repeating itself verbatim. Lastly, examples verify that AIS evaluations can be disentangled from other quality aspects, such as conversational relevance. This was challenging to instruct to annotators as it is instinctual to judge quality more holistically, and they were explicitly given instructions with multiple examples illustrating what types of quality aspects to ignore. In the resulting annotations, they would mark incoherent summaries or irrelevant conversational replies as AIS if they conveyed well supported information, appropriately disregarding other aspects of quality.

<table><tr><td>Table 12Examples of reference (i.e. gold) text that was marked by annotators as interpretable but not AIS.</td></tr><tr><td>Example 1. (CNN/DM)Summary (Reference)thomas piermayr has been training with blackpool this week .austrian defender is a free agent after leaving mls side colorado rapids .blackpool are bottom of the championship and look set to be relegated ..Attributed DocumentBlackpool are in talks to sign Austria defender Thomas Piermayr.The 25-year-old has been training with the Championship club this week and they are keen to get him on board for what is expected to be confirmed as a campaign in League One next season.Piermayr is a free agent and had been playing for Colorado Rapids.The former Austria U21 international had a spell with Inverness Caledonian Thistle in 2011.Thomas Piermayr (left, in action for the Colorado Rapids) tries to tackle Obafemi Martins last year ..Explanation: The article doesn&#x27;t mention Blackpool being the bottom of the championship but it is included in the gold summary. Possibly the journalist who wrote the article highlights (that the summary data was extracted from) included that sentence because they were assuming that the sports section audience might already be aware of the standings.</td></tr><tr><td>Example 2. (Wizard of Wikipedia)Queryi really love kentucky, i was born and raised here, have you ever been there?Response (Reference)my parents are from kentucky! i have only been to east, south-central region state a few times.Attributed Documentkentucky (, ), officially the commonwealth of kentucky, is a state located in the east south-central region of the united states.Explanation: the original interlocutor relayed some information from the document and also embellished with their own personal experiences (that are not verifiable) to make a more engaging conversation.</td></tr><tr><td>Example 3. (QReCC)Querywhat musical has the song you&#x27;ll never walk aloneResponse (Reference)you&#x27;ll never walk alone is a show tune from the 1945 rodgers and hammerstein musical carousel.Attributed Documentliverpool is one of the best supported clubs in the world.the club states that its worldwide fan base includes more than 200 officially recognised club of the lfc official supporters clubs in at least 50 countries. notable groups include spirit of shankly.the club takes advantage of this support through its worldwide summer tours, which has included playing in front of 101,000 in michigan, u.s., and 95,000 in melbourne, australia.liverpool fans often refer to themselves as kopites , a reference to the fans who once stood, and now sit, on the kop at anfield. in 2008 a group of fans decided to form a splinter club, a.f.c. liverpool , to play matches for fans who had been priced out of watching premier league football.the song &quot; you&#x27;ll never walk alone &quot;, originally from the rodgers and hammerstein musical carousel and later recorded by liverpool musicians gerry and the pacemakers , is the club&#x27;s anthem and has been sung by the anfield crowd since the early 1960s.it has since gained popularity among fans of other clubs around the world.the song&#x27;s title adorns the top of the shankly gates, which were unveiled on 2 august 1982 in memory of former manager bill shankly.the &quot;you&#x27;ll never walk alone&quot; portion of the shankly gates is also reproduced on the club&#x27;s crest.Explanation: The year &quot;Carousel&quot; was made (1945) cannot be attributed to the selected passage. The original interlocutor may have seen that detail elsewhere.</td></tr></table>

## 6. Discussion

Generative models have been advancing toward human-like competence in some aspects. Their real-world application in consumer-focused information products are becoming more attractive, for example, for summarizing original descriptions of events, or for deriving answers to pertinent questions about the world. Traditionally, this type of information transformation has been performed by specialized human experts (e.g., journalists, researchers), who are required to meet a variety of standards of accuracy and accountability, maintaining one or more sources for a proposition and performing fact-checking. The task could also be likened to the practice of law, where norms are examined for their subsumptive relationship to a set of circumstances, and where both close reading and a set of conventionalized tests aid this determination.

We formalize a specific sub-task of fact-checking, namely, verification against a known source, as a necessary but not sufficient step in ensuring the quality of generated text. We show that with the right training, careful instructions, and optimized user interfaces, we can delegate the judgment of attribution to underlying source(s) to crowd workers, but we also find limitations. Following the data collection we described, we found it necessary to set some standards in our instructions to raters. This includes setting expectations for named entities, for example, whether first and last names are needed to identify an individual and to link them between evidence and statement, or if a place name without qualification may be acceptable as long as there are no other wellknown places of the same name. Similarly, as statements and evidence become more complex, raters inevitably draw inferences using individual world knowledge. This is unavoidable and is inherently noisy (Pavlick and Kwiatkowski 2019); ground truth is ambiguous, just like journalists, researchers, or judges often legitimately disagree. Possible model outputs fall on a spectrum ranging from synthesized information to the mostly unassailable extractive generations (Ladhak et al. 2022). AIS does not set policy about where model output should fall: its users still need to decide where to draw the line.

AIS is limited to propositions that can be judged with the “according to” framework. AIS is not applicable to questions (without presuppositions) or imperatives (commands and requests). There are also scenarios where strict attribution contradicts other desirable output characteristics (e.g., chit–chat systems). We did not examine AIS on such data. How to evaluate hybrid systems that mix entertaining and informative communicative goals — capturing the attribution of the informative portion but ignoring the rest — is unclear, as is the question of whether systems with blurry boundaries between what is and is not subject to attribution should exist at all.

We have purposefully limited the availability of context in our definition. Practical human–computer interactions may actually take place in context beyond the shared time t that is used in the definition (Section 3), perhaps because the communication channel is richer than a text-based line of transmission, and because it may be further extended by multi-session interaction history. It is important that annotators remain aware of the notion of explicature, resolving explicit references and implicit topics available to the communicators. It is possible that the use of models that perform this task (Choi et al. 2021) can improve the performance of raters. We are also aware that this task requires close reading, which is challenging to implement on crowdsourcing platforms where speed, efficiency, and cost are incentivized instead. Again, models may be useful in extracting explicit, elementary propositions from complex statements, making this task easier for raters. We will examine such approaches in future work.

## 7. Conclusion

In this paper, we define a new evaluation framework called Attributable to Identified Sources which allows us to inspect whether information in generated text can be supported by source documents. We provide formal definitions of AIS and descriptions of how it can be applied to three different NLG tasks (conversational QA, summarization, and table-to-text generation). We validate this evaluation framework quantitatively on human evaluation studies, in which annotators rated the AIS of model output as part of a two-stage annotation pipeline. The results of the human evaluation studies demonstrate that high-quality AIS ratings can be obtained empirically. The results shed light on some of the ongoing challenges in training NLG models; having solid AIS is the basis for addressing them.

<table><tr><td>Table 1Examples marked by annotators as uninterpretable.</td></tr><tr><td>Example 1. (Wizard of Wikipedia)Conversation HistoryAPPRENTICE: hi, can you tell me about parenting?WIZARD: its the process of promoting and supporting the physical, emotional, social, and intellectual development of your kid, its really important for kidsAPPRENTICE: thats fair enough, do you have kids?WIZARD: no, but i am planing to have a big family one day, i really like the thought of raising a childQueryyeah i dont have kid's but i'm really looking forward to it soon. when do you think is a good age to have kids?Response (T5 with Controls)a good parent may be referred to as a "good parent"Rating: Not Interpretable</td></tr><tr><td>Example 2. (QReCC)Queryhow did the wildhearts band members meet each other?Response (T5-Small Pretrained)gingerRating: Not Interpretable</td></tr><tr><td>Example 3. (CNN/DM)Summary (Reference)daniel andersson , helsinborg 's 42-year-old kit man , kept a clean sheet .the emergency stopper played in season opener against kalmar .henrik larsson 's first-choice goalkeepers were both out injured .the former goalkeeper earned one cap for sweden back in 2001 .Rating: Not Interpretable (Note: This is actually a reference summary. Annotators selected this as unclear as it is difficult to understand on its own. The original journalist writing this may haveassumed some amount of commonsense/background knowledgeabout football/soccer for the intended audience as well as other information such as what games were being played that day. The interpretability judgement could varydepending on annotators' familiarity with the topic.)</td></tr><tr><td>Example 4. (CNN/DM)Summary (Pointer-Generator Network)ivan carlos , 22 , and eighteen-year-old brenda avilez , 18 , were sleeping in a trailer at the lone oak mobile home in palmetto at 2.30am wednesday .the driver of the white chevrolet suv lost control of the vehicle and crashed through the fence at the lone oak mobile home in palmetto .avilez was nine months pregnant at the time , the herald reports , the fetus did not survive .crawford , 21 , was taken to a hospital with non-life-threatening injuries .Rating: Not Interpretable (Note: There's some degenerate/repetitive language (18, eighteen) as well asunclear references that lack context ("the white chevrolet suv"). )Table 2Examples marked by annotators as interpretable but not AIS.</td></tr><tr><td>Example 1. (Wizard of Wikipedia)Conversation HistoryWIZARD: my pet horse is named beauty. she's domesticated :)APPRENTICE: that must be awesome to have a pet horse! do you ride it?WIZARD: yeah! we're not sure what breed she is, because we rescued her, but there are all sorts of different types of breeds and sizes of horses.Queryhow many different breeds are there? what color is your horse?Response (T5-Base)i'm not sure, but there are a lot of domesticated horses, but some feral ones are wild.Attributed Documenthorses in the subspecies "caballus" are domesticated, although some domesticated populations live in the wild as feral horses.Rating: Interpretable, not AIS</td></tr><tr><td>Example 2. (QReCC)Conversation HistoryUSER:are there any other interesting aspects about ann veneman?SYSTEM: ann veneman has received several awards and distinctions throughout her career.Querywhat kind of awards has ann veneman won?Response (T5-Small)in 2009, ann veneman received the award of distinction from the university of california davis college of agricultural and environmental sciences.Attributed DocumentIn 2009, she received the award of distinction from the university of california davis college of agricultural and environmental sciences. veneman is an honorary member of rotary international (2008), received sesame workshop's leadership award for children (2006), and a humanitarian award from the united nations association of new york (2006). ...Rating: Interpretable, Not AIS (Note: The information is partially represented in the document but there's some referential ambiguity as the document only refers to "she" and "veneman" but it is unclear whether it's referring to "Ann Veneman" specifically. 3 of 5 annotators marked this as not AIS.)</td></tr><tr><td>Example 3. (QReCC)Conversation HistoryUSER: when was the verve's fiirst break up?SYSTEM: the verve's turmoil continued into 1995's a northern soul. the album reached the uk top 20 in july, but ashcroft broke up the band three months later, just before history.USER: was history by the verve a success?SYSTEM: history was released 18 september 1995 as the third and final single from a northern soul, charting at #24 in the uk singles chart.Querywhat other album was released by the verve besides a northern soul?Response (T5-Small without Evidence)the verve's turmoil continued into 1995's a northern soul.Attributed Documentcommercial success and second break-up (1997–1999) in early 1997, ashcroft asked mccabe to return, stating: "i got to the point where nothing other than the verve would do for me". mccabe obliged and with the new line-up in place (tong remained on guitar alongside mccabe), the group went through a "spiritual" recording process to finish their third album urban hymns which was completed by early summer. "bitter sweet symphony" the first track on their album urban hymns, " bitter sweet symphony " is renowned for its signature swirling orchestral melody. problems playing this file? see media help ...Rating: Interpretable, Not AIS (Note: On a surface-level, the information seems plausibly informative but is not supported in the provided document. This is actually only superficially repeating a previous conversation turn. 5 of 5 annotators marked this as not AIS.)</td></tr><tr><td>Table 3Examples marked by annotators as interpretable and AIS.</td></tr><tr><td>Example 1. (Wizard of Wikipedia)Conversation HistoryWIZARD: what do you know about the chevrolet corvette?Response (T5-Base)well, it's a sports car manufactured by chevrolet.Attributed Documentthe chevrolet corvette, known colloquially as the vette or chevy corvette, is a sports car manufactured by chevrolet.Rating: Interpretable, AIS</td></tr><tr><td>Example 2. (QReCC)Conversation HistoryUSER: what is the british invasion in music?SYSTEM: the british invasion was a cultural phenomenon of the mid-1960s, when rock and pop music acts from the united kingdom and other aspects of british culture, became popular in the united states and significant to the rising counterculture on both sides of the atlantic.Querywhat era did the british invasion in music happen?Response (T5-Base)pop and rock groups such as the beatles, the rolling stones, the kinks, the dave clark five, herman's hermits, the zombies, and the animals were at the forefront of the british invasion.Attributed Document... the british invasion was a cultural phenomenon of the mid-1960s, when rock and pop music acts from the united kingdom and other aspects of british culture became popular in the united states and significant to the rising "counterculture" on both sides of the atlantic. pop and rock groups such as the beatles, the rolling stones, the kinks, the dave clark five, herman's hermits, the zombies, and the animals were at the forefront of the "invasion"....Rating: Interpretable, AIS (Note: AIS is a focused metric on one dimension of quality. This response is AIS even though it fails inother dialogue qualities, i.e. relevance to previous query.)</td></tr><tr><td>Example 3. (CNN/DM)SummaryGary Johnson took over as Cheltenham Town manager on March 30 .He asked his players to write 'I promise to do all I can to keep Cheltenham Town in the league' on an A3 sheet of paper .'Some signed it and meant it, and some signed it and didn't mean it,' Johnson said .Attributed DocumentCheltenham Town have two games to preserve their Football League status - and managerGary Johnson has revealed one of the techniques he is using to try and bring the best out of his players.When Johnson took over as manager of the League Two club on March 30, he wrote 'I promise to do all I can to keep Cheltenham Town in the league' on an A3 sheet of paper and asked his players to put their signature on it.'They all signed it,' Johnson said to the BBC. 'Some signed it and meant it, and some signed it and didn't mean it.Cheltenham Town manager Gary Johnson got every payer to pledge to give his all when he took over .Cheltenham were beaten by Northampton in their last game and have two games left to try and stay up .'When you come to this stage of the season you need everyone to give everything for the cause,' Johnson added.'You also need team-mates you can rely on. The lads that are here need to know they can rely on the others - and if they can't rely on some then you have to move them on.'Cheltenham occupy 23rd in League Two and trail 22nd placed Hartlepool United and the safety places by a point.Their final two games are against second placed Shrewsbury and 13th placed Wimbledon.Rating: Interpretable, AIS</td></tr></table>

![](images/598cfc952edfbcd2f2a7aaf1c9f4f5f0b37fd8afd1e1651b353cd62e7affd793.jpg)

## Example 1: Uninterpretable statements

The population was 798 at the 2010 census, up from 648 at the 2000 census.

## Example 2: Interpretable but NOT AIS

## Manny Trillo

Explanation: column header abbreviations don’t match statement

## Example 3: Interpretable but NOT AIS

1877 New York state election

<table><tr><td>Ticket / Office</td><td>Secretary of State</td><td>Comptroller</td><td>Attorney General</td><td>Treasurer</td><td>State Engineer</td></tr><tr><td>Democratic</td><td>Allen C. Beach 383,062</td><td>Frederic P. Olcott 395,701</td><td>Augustus Schoonmaker, Jr. 383,367</td><td>James Mackin 384,040</td><td>Horatio Seymour, Jr. 395,321</td></tr><tr><td>Republican</td><td>John C. Churchill 371,798</td><td>Clinton V. R. Ludington 359,590</td><td>Grenville Tremain 371,826</td><td>William L. Bostwick 370,383</td><td>Howard Soule 360,157</td></tr><tr><td>Working Men</td><td>John J. Junio 20,282</td><td>George Blair 19,123</td><td>Warren T. Worden 19,538</td><td>Samuel G. Rice 18,480</td><td>Walter T. Griswold 19,653</td></tr><tr><td>Prohibition</td><td>Henry Hagner 7,230</td><td>Elias T. Talbot 7,444</td><td>G. Havens Gleason 7,291</td><td>Joseph W. Grosvenor 7,383</td><td>Henry D. Myers 7,386</td></tr><tr><td>Social Democratic</td><td>John McIntosh 1,799</td><td>G. Kuhne 1,271</td><td>Ernst Smith 1,348</td><td>R. H. Bartholomew 1,827</td><td>C. F. Collenburg 1,356</td></tr><tr><td>Greenback</td><td>Francis E. Spinner 997</td><td>Thomas B. Edwards 973</td><td>William S. Jaynes</td><td>William Doyle 920</td><td>Rushton Smith</td></tr><tr><td>German Independent</td><td>John C. Churchill</td><td>Frederic P. Olcott</td><td>Grenville Tremain</td><td>William L. Bostwick</td><td>Horatio Seymour, Jr.</td></tr><tr><td>Bread-Winners</td><td>John J. Junio</td><td>Frederic P. Olcott</td><td>Elmore Sharpe</td><td>Julius Kern</td><td>Horatio Seymour, Jr.</td></tr></table>

Explanation: The candidates listed in this row were running for different positions (on the same party ticket). Comparing to the rest of the column, it seems that Churchill actually lost.

## Example 4: AIS

Drunk on Love (Rihanna song)

Section Title: Charts

South Korea (Gaon Chart) 55

UK Singles Chart (OCC) 153

Model Output

ByT5-xl Drunk on Love (Rihanna song) peaked at number 153 on the UK Singles Chart in 2011.

Figure 1 Examples from the table-to-text annotations.

## Appendix B: Evaluation Instructions for Conversational Question Answering

The following is a verbatim representation of the instructions that were presented to paid crowd annotators for performing the task alongside the interface. The prompts in the rating interface include wording from the instructions; the rating interface also contains hyperlinks to example sections in the instructions for each question and rating.

## Overview

In this task you will evaluate the quality of a system-generated response to a user query. The system is trying to help the user learn about a particular topic by answering their questions. We want to rate the system response quality based on how well it represents the original source.

We will be using two categories to evaluate the quality of the summary: Interpretability and Attribution. You will evaluate these categories in succession. Some ratings will result in other categories being skipped. The task interface will guide you through the flow; you can also see the overall task flow in the diagram below.

![](images/c210a48a8eba47491ace49e8471818e0e652df4654dd32e2c11febecda6c9d1a.jpg)

Note: The system-generated responses may appear very fluent and well-formed, but contain slight inaccuracies that are not easy to discern at first glance. Pay close attention to the text. Read it carefully as you would when proofreading.

The sections below describe each of the dimensions in detail. You can also flag ineligible tasks; the flagging criteria are described in this section.

## 1. Interpretability

In this step you will evaluate whether the system response is interpretable by you.

You will be shown an excerpt of a conversation between a user and an assistant-like computer system. The last turn in the conversation will be a user query from the user followed by a system response attempting to respond to their query. Given the context of the user query, carefully read the system response and answer the following question:

## (Q1) Is all of the information relayed by the system response interpretable to you?

This is asking whether you can understand the response. If there is some part of the response that is unclear or hard to interpret, select “No”. If prompted by the interface, enter a succinctly detailed justification of your rating.

Definition:. An uninterpretable response has diminished intelligibility due to:

• Vague or ambiguous meaning, e.g., unclear pronouns usage.

• Malformed phrases and sentences that are difficult to understand.

If the system response is interpretable by you, you will proceed to the next category. Examples of interpretability ratings and justifications are in this section.

## 2. Attribution

In this step, you will evaluate how well a system-generated response is attributable to the source document. Note that the source document is a new element that will appear in the task only when you reach this question.

Note: We refer to “attributable to source document” interchangeably as “attribution” and “supported by the source document”. By which we mean, all of the information in the system response can be verified from the source document.

You will be shown an excerpt of a conversation between a user and an assistantlike computer system. The last turn in the conversation will be a user query from the user followed by a system response attempting to reply to their query. You will also be shown a document that was cited by the system as its source in attempting to answer the question (source document). You will use all three (user query, system response, source document) to answer the following question:

(Q2) Is all of the information provided by the system response fully supported by the source document?

This is asking whether all of the information in the system response can be attributed to the information present in the source document. If prompted by the interface, enter a succinctly detailed justification of your rating.

Definition:. Attribution of system-generated response in relation to the source document can be established by considering the following:

## A. What is the information provided by the system response?

## B. Is this information an accurate representation of information in the source document?

A. Definition of “the Information Provided by the System Response”. Two points are key in determining the information provided by the system response:

1. The context of the system response — that is, the query and previous conversation turns — is often critical in determining the “information provided by the system response”.

2. The source document should be completely ignored when determining “the information provided by the system response.” (i.e., it should not be used as additional context).

## Consider the following example:

User query

who plays doug and julie in days of our lives

System response

In the American daytime drama Days of Our Lives, Doug Williams and Julie Williams are portrayed by Bill Hayes and Susan Seaforth Hayes

In the above example, the meaning of the system response is clear even without seeing the query. But consider another example: User query who plays doug and julie in days of our lives System response he is played by Bill Hayes

In this case the pronoun “he” depends on the context (i.e., the query): but it is clear that the intended meaning of the system response can be paraphrased as something along the lines of “Doug Williams in days of our lives is played by Bill Hayes”. In this case this paraphrase is the “information provided by the system response”.

Pronouns such as he/she/it/they etc. are one case where context is needed to figure out the intended meaning of the system response. Other examples are the following (given with paraphrases of the information that is provided by the system response): User query 1 which network is days of our lives on System response 1 the show is on NBC Paraphrase of information provided by system response days of our lives is on NBC User query 2 which network is days of our lives on System response 2 NBC Paraphrase of information provided by system response days of our lives is on NBC User query 3 how many seasons are there of days of our lives System response 3 there are 56 seasons Paraphrase of information provided by system response there are 56 seasons of days of our lives

In system response 1, the phrase “the show” needs context for interpretation, but it is clear from the context of the query that it refers to “days of our lives”. In system response 2, the system gives a direct answer to the query, simply “NBC”, but it is clear given the query that the information provided by the system is “days of our lives is on NBC”. In query 3, the phrase “56 seasons” needs context for interpretation, but given the query it is clear that the response is referring to “56 seasons of days of our lives”.

In general, use your best judgment to determine the information provided by the system response. If you are unsure what the intended meaning is of the system response, make sure that you marked the example as “No, the response is unclear.” as part of the Interpretability stage. As one example, take the following:

User query how many NBA championships did Michael Jordan win? System response it is the best team in the NBA Paraphrase of information provided by system response meaning is unclear

In this case it is not clear what “it” is referring to, and the meaning should be marked as being unclear. Again, use your best judgment in determining whether or not the meaning of the system response is clear.

B. Definition of “An Accurate representation of Information in the Source Document”. Again, you should use your best judgment in determining whether all of the information provided by the system response is “an accurate representation of information in the source document”. We give the following guidance:

In determining this question, ask yourself whether it is accurate to say “the document says. . . ” or “according to the document. . . ” with the system response following this phrase. For example, is it accurate to say “according to the document below, In the American daytime drama Days of Our Lives, Doug Williams and Julie Williams are portrayed by Bill Hayes and Susan Seaforth Hayes” in the example given above?

Be sure to check all of the information in the response. If only some of the information is supported in the document, but other parts of the information are missing from the document or not an accurate representation, then please mark “No, not fully attributable.”

The concept of “accurate representation” should be close to a journalist’s conception of this phrase. For example take this excerpt from this page on Accuracy in the NPR Ethics Handbook: “When quoting or paraphrasing anyone. . . consider whether the source would agree with the interpretation. . . ” In other words, if you had written the source document, consider whether you would view the system response as an accurate representation of information in that source document.

## Some Final Important Notes.

Source quality.. When making your judgments in this template, do not take into account whether the underlying source document is correct or trustworthy. This is clearly important, but will be evaluated in a separate task. The “attribution” category is used only to judge whether the information provided by the system response is an accurate representation of the underlying source document.

Context and relevance.. Additionally, when rating attribution, do not take into account the degree of relevance of the system response to the user query. Partially and fully relevant responses can be equally assessed for attribution, regardless of how much information contained in them is relevant to the query. In both cases you should judge whether or not the system responses are an accurate representation of information in the source document even if it doesn’t perfectly address the question.

Examples of attribution ratings and justifications are in this section.

## Scoring and Examples

## Interpretability

No, the response is unclear:. The response is unclear and/or difficult to understand.

<table><tr><td>User querywhen was the last time it snowed in england on christmas day</td></tr><tr><td>System responseit was in 2009, but it was white</td></tr><tr><td>JustificationThe answer contains the pronoun “it” with an unclear meaning; it also sets up a contrasting statement with “but”, which is hard to interpret.</td></tr><tr><td>User querywho sings in walk hard the dewey cox story</td></tr><tr><td>System responsehe and john c. Reilly sang all the songs and played guitar on most of them.</td></tr><tr><td>JustificationThe answer contains the pronoun “he” with an unclear meaning.</td></tr><tr><td>User querywhat event marks the beginning of the great depression</td></tr><tr><td>System responseafter a major fall in stock prices that began around september 4, 1929, and became worldwide news with the stock market crash of October 29, 1929</td></tr><tr><td>JustificationThe answer is malformed and difficult to interpret: the sentence appears to be missing the subject somewhere near “and became”.</td></tr></table>

## Attribution

Yes, fully attributable:. All of the information in the system response is supported by the document.

when did the subway open in new york

the subway was first opened in 1904

The New York City Subway is a rapid transit system owned by the City of New York and leased to the New York City Transit Authority, a subsidiary agency of the state-run Metropolitan Transportation Authority (MTA). Opened in 1904, the New York City Subway is one of the world’s oldest public transit systems, one of the world’s most used metro systems, and the metro system with the most stations. It offers service 24 hours per day on every day of the year.

The information in the response is accurately representing the document.

No, not fully attributable:. The response contains any amount of information that is not supported by the document (including responses that are only partially or not at all supported).

## User query

when did the subway open in new york

## System response

the subway was first opened in late 1904.

## Source document

The New York City Subway is a rapid transit system owned by the City of New York and leased to the New York City Transit Authority, a subsidiary agency of the state-run Metropolitan Transportation Authority (MTA). Opened in 1904, the New York City Subway is one of the world’s oldest public transit systems, one of the world’s most used metro systems, and the metro system with the most stations. It offers service 24 hours per day on every day of the year.

## Justification

The document confirms that it was opened in 1904 but it doesn’t specify if it was “late 1904”.

## User query

who has the most all star mvp awards

## System response

bob pettit, kobe bryant, oscar robertson, michael jordan, shaquille o’neal, and lebron james have all won the award four times.

## Source document

Bob Pettit and Kobe Bryant are the only two players to win the All-Star Game MVP four times. Oscar Robertson, Michael Jordan, Shaquille O’Neal, and LeBron James have each won the award three times.

## Justification

The cited document only supports Bob Petit and Kobe Bryant. The others listed only won the award three times according to the document.

## User query

who expanded the palace of versailles to its present size

## System response

louis xiv, his successor, was a very good person.

## Source document

Louis XIII’s successor, Louis XIV, had a great interest in Versailles. He settled on the royal hunting lodge at Versailles, and over the following decades had it expanded into one of the largest palaces in the world. Beginning in 1661, the architect Louis Le Vau, landscape architect André Le Nôtre, and painter-decorator Charles Lebrun began a detailed renovation and expansion of the château. This was done to fulfill Louis XIV’s desire to establish a new centre for the royal court. Following the Treaties of Nijmegen in 1678, he began to gradually move the court to Versailles. The court was officially established there on 6 May 1682.

## Justification

The answer is correct but the last part (he was a “very good person”) is an opinion and not supported by the document.

## Flag

There is a flag button in the bottom left corner of the task interface. Once flagged, you can proceed onto the next task. Use it report tasks that are ineligible for reasons such as:

1. Missing components in the task.. Some tasks may have missing user queries, responses or source text. They should be flagged.

2. Malformed text.. Some text may be severely malformed with unintelligible artifacts (e.g. html code, unformatted tables, etc.). If any component of the task contains malformed text, the task should be flagged. The example below shows various types of malformed text.

i think it took place in a gymnasium in san diego, where the black students auditioned to play for the \$team\_winner until boone arrives, but the meeting turns into a fiasco when yoast and white students interrupt.

## Source document

The black students have a meeting in the gymnasium in auditioning to play for the team until &amp;&amp;&amp;&amp;Boone&amp;&amp;&amp;&amp;&amp; arrives, but the meeting turns into a fiasco when Yoast and white students interrupt. On August 15, 1971, the players gather and journey to Gettysburg College, where their training camp takes place.

3. Source document is underspecified.. Some source documents may not have sufficient information to determine whether it does/doesn’t support the response. They may be too short and/or lack critical information that would be necessary to rate the response.

<table><tr><td>User querywhere is the hero golf challenge being played</td></tr><tr><td>System responsethe event will be held at the Albany development in the Bahamas</td></tr><tr><td>Source documentBeginning in 2015, the event will be played at the Albany development in the Bahamas, for at least three years.</td></tr><tr><td>JustificationThe source document does not specify what event it is referring to, and so it&#x27;s impossible to determine whether this is referring to the same “hero golf challenge” or not . Without the explicit mention of “hero gold challenge”, the task should be flagged.</td></tr><tr><td>User querywho is known as the super fast boy in the series the incredible</td></tr><tr><td>System responsespencer fox as dashiell robert parr</td></tr><tr><td>Source documentSpencer Fox as Dashiell Robert Parr / Dash, the Parrs’ second child, who possesses super-speed</td></tr><tr><td>JustificationIt’s unclear whether the source document is referring to the same character as the one in the query because it does not specify the series (“the incredible”) or the name of the character (“the super fast boy”).</td></tr></table>

4. Source document is difficult to understand because it requires expert-level knowledge.. Some documents may include scientific formulas, obscure terminology, etc. If you can still understand enough of the document to rate the attribution, please do so. But, on the other hand, if properly evaluating the response requires expertise in a particular area, please flag it.

## User query

what is the rate limiting enzyme of kreb’s cycle

## System response

kreb is the enzyme that uses fad as a prosthetic group

## Source document

Substrates Products Enzyme Reaction type Comment 0 / 10 Oxaloacetate + Acetyl CoA + H2O Citrate + CoA-SH Citrate synthase Aldol condensation irreversible, extends the 4C oxaloacetate to a 6C molecule 1 Citrate cis-Aconitate + H2O Aconitase . . .

## Justification

In order to be able to evaluate whether this source document supports the response, it requires a deeper understanding of scientific equations and terminology contained in th document. Because this example requires scientific expertise to evaluate it properly, it should be flagged.

## Appendix C: Evaluation Instructions for Summarization

The following is a verbatim representation of the instructions that were presented to paid crowd annotators for performing the task alongside the interface. The prompts in the rating interface include wording from the instructions; the rating interface also contains hyperlinks to example sections in the instructions for each question and rating. The summarization instructions were developed after the conversational QA instructions had been established and the annotators had been trained on the conversation QA task.

## Overview

In this task you will evaluate the quality of a system-generated summary. The system’s goal is to summarize the source news article, while remaining truthful to it. We want to rate the quality of the summary based on how well it represents the original source.

We will be using two categories to evaluate the quality of the summary: Interpretability and Attribution. You will evaluate these categories in succession. Some ratings will result in other categories being skipped. The task interface will guide you through the flow; you can also see the overall task flow in the diagram below.

![](images/dbee22d25e081715b1865b8616dde5f9f07bb68f66ebb55b14b88616b89d3dee.jpg)

Note: The system-generated summaries may appear very fluent and well-formed, but contain slight inaccuracies that are not easy to discern at first glance. Pay close attention to the text. Read it as carefully as you would when proofreading.

The sections below describe each of the dimensions in detail. You can also flag ineligible tasks; the flagging criteria are described in this section.

## 1. Interpretability

In this step you will evaluate whether the system summary is interpretable by you.

You will be shown a system-generated summary of a news article. Note that the news article from which the summary is derived is hidden at this step, because we need to evaluate whether the summary is interpretable on its own. Carefully read the summary and answer the following question:

## (Q1) Is all of the information relayed by the system summary interpretable to you?

This is asking whether you can understand the summary on its own. If there is any part of the summary that is unclear or hard to interpret, select “No”. If prompted by the interface, enter a succinctly detailed justification of your rating.

Definition:. An uninterpretable summary has diminished intelligibility due to:

• Vague or ambiguous meaning, e.g., unclear noun references or pronouns usage.

• Malformed phrases and sentences that are difficult to understand.

If the summary is interpretable by you, you will proceed to the next category.

In the section below, we show in more detail the kind of reasoning that should be used for establishing interpretability of summaries. More examples of interpretability ratings and justifications are in this section of the appendix.

Interpreting the information provided in the system summary. Consider the following example:

## Summary

seismologists put the magnitude at 7.9 for an earthquake that hit kathmandu today, which would actually make it about 40% larger than the 7.8 currently being reported .

In the above example, the meaning of the summary is clear even without seeing the original news article. It is clear what the summary is reporting on and it stands on its own, that is, this summary is interpretable. It should be marked as “Yes, I understand it.” But consider another example:

## Summary

seismologists put the magnitude at 7.9 , which would actually make it about 40% larger than the 7.8 currently being reported .

In this case the meaning of the phrase “the magnitude” obviously depends on some context, but that context is missing in the summary. Without additional information that clarifies that the magnitude refers to an earthquake that occurred in a specific location (Kathmandu), the summary is difficult to interpret and it does not stand on its own. It should be marked as “No, the summary is unclear.”

Noun phrases that require clarifications of this kind are one case where interpretability can be diminished. Other examples include nouns and pronouns without a (clear) reference and malformed phrases and sentences:

## Summary 1

the project is hoped to open at the former arts centre , la llotja . friend and producer jaume roures of mediapro is leading the tribute . the museum follows allen ’s vicky cristina barcelona, set in the city

## Summary 2

new england patriots tight end aaron hernandez has pleaded not guilty to murder and two weapons charges . he ’s accused of orchestrating the shooting death of odin lloyd . it ’s scheduled to begin in may , but not legally required to get a conviction .

## Summary 3

john stamos announced monday night on “ jimmy kimmel live ” . the show will feature candace cameron bure , who played eldest daughter d.j . tanner in the original series , which aired from 1987 to 1995 , will both return for the new series

In summary 1, the phrase “the project” needs context for interpretation (“what project is being reported on?”). Likewise, “the museum” and “the city” are unclear (“what museum is this?”, “what city is this taking place in?”). In summary 2, the system provides a clear reference for the pronoun “he” (“hernandez”), but a reference for the pronoun “it” is missing (“what is scheduled to begin in may?”). Also it is not clear what “not legally required to get a conviction” is referring to. In summary 3, the first sentence is malformed because it is missing the announcement (“what did john stamos announce?”). The second sentence is difficult to understand (“who does ‘both’ refer to?”, “who will return to the new series?”).

In general, use your best judgment to determine the information provided by the summary. If you are unsure what the intended meaning of the summary is, err on the side of marking it with “No, the summary is unclear.”

## 2. Attribution

In this step, you will evaluate how well a system-generated summary is attributable to the source news article. Note that the source news article is a new element that will appear in the task only when you reach this question.

Note: We refer to “attributable to the source news article” interchangeably as “attribution” and “supported by the source news article”. By which we mean, all of the information in the system-generated summary can be verified from the source news article.

You will be shown a system-generated summary of a news article. You will also be shown the news article that was used by the system to generate this summary (source news article). You will use both of these to answer the following question:

(Q2) Is all of the information provided by the system summary fully supported by the source document?

This is asking whether all of the information in the system summary can be attributed to the information present in the source news article. If prompted by the interface, enter a succinctly detailed justification of your rating.

Definition:. a fully supported (or attributable) system-generated summary contains an accurate representation of information in the source news article. No information in the summary is unattested when compared against the source news article.

In the section below, we show in more detail the kind of reasoning that should be used for establishing attribution of summaries. More examples of attribution ratings and justifications are in this section of the appendix.

Assessing the accuracy of the information in the summary against the original news article. Again, you should use your best judgment in determining whether all of the information provided by the system summary is “an accurate representation of information in the source news article”. We give the following guidance:

In determining this question, ask yourself whether it is accurate to say “the provided news article says. . . ” or “according to the news article. . . ” with the system summary following this phrase.

Be sure to check all of the information in the summary. If only some of the information is supported in the news article, but other parts of the information are missing from the news article or not an accurate representation, then please mark “No, not fully attributable.”

The concept of “accurate representation” should be close to a journalist’s conception of this phrase. For example take this excerpt from this page on Accuracy in the NPR Ethics Handbook: “When quoting or paraphrasing anyone. . . consider whether the source would agree with the interpretation. . . ” In other words, if you had written the source document, consider whether you would view the summary as an accurate representation of information in that source document.

## Some Final Important Notes.

Source quality.. When making your judgments in this template, do not take into account whether the underlying source news article is correct or trustworthy. This is clearly important, but will be evaluated in a separate task. The “attribution” category is used only to judge whether the information provided by the system summary is an accurate representation of the underlying source news article.

Examples of attribution ratings and justifications are in this section.

## Scoring and Examples

## Interpretability

No, the summary is unclear:. The summary is unclear and/or difficult to understand.

## Summary

The bill would prevent adolescents from smoking, buying or possessing both traditional and electronic cigarettes . The bill includes a \$10 fine for first-time offenders. Subsequent violations would lead to a \$50 fine or mandatory community service . Dozens of local governments have similar bans, including Hawaii County and New York City .

## Justification

The summary revolves around the noun phrase “the bill” that doesn’t have a clear reference (what bill is it referring to?); it makes the summary difficult to understand fully.

## Summary

The former England rugby star tweeted ‘Holy s\*\*\*, I’m lost for words and emotions. All I can say is yes the dude!!!!!’ After he bought the horse Zara called him an idiot, but she was there with him, cheering the horse home . Monbeg Dude was given the all-clear to run in the Grand National at Aintree after a poor showing at the Cheltenham Festival.

## Justification

The answer contains the noun phrase “the former England rugby star” that lacks a clear reference (who is it?). Furthermore, the usage of pronouns “he”, “him” and “she” is too vague (who are they referring to in the summary?).

## Summary

john stamos announced monday night on “ jimmy kimmel live ” . the show will feature candace cameron bure , who played eldest daughter d.j . tanner in the original series , which aired from 1987 to 1995 , will both return for the new series

## Justification

The answer is malformed and difficult to interpret. The first sentence is missing the object of “announced” (what did john stamos announce?). Additionally, “will both return for the new series” appears to be poorly connected to the previous context.

## Attribution

Yes, fully attributable:. All of the information in the system summary is supported by the document.

## Summary

Convicted murderer Nikko Jenkins, 28, tried to carve ’666’ into his forehead . But in a phenomenal case of idiocy, he used a mirror - so the numbers came out backwards . The symbol is described in the biblical book of Revelation as ’the sign of the beast’, and has since been popularized by the horror movie The Omen . Jenkins was jailed exactly one year ago for shooting dead four people in 10 days after being released from prison .

## Original news article

C It was meant to be the ultimate symbol of menace: carving ’666’ into his forehead.

But in a phenomenal case of idiocy, convicted murderer Nikko Jenkins used a mirror - so the numbers came out backwards.

The symbol is described in the biblical book of Revelation as ’the sign of the beast’, and has since been popularized by the horror movie The Omen.

However, with a series of upside-down 9s, Jenkins has fashioned himself an entirely unique - and irreversible - engraving.

Botched: Nikko Jenkins (pictured in 2014) recently tried to carve ’666’ into his forehead but did it backwards .

According to Omaha.com, Jenkins told his attorney about the incident in a phone call from his cell in Omaha, Nebraska.

It comes amid the 28-year-old’s ongoing appeal that he is mentally unstable and therefore ineligible to face the death penalty.

Jenkins was jailed exactly one year ago for shooting dead four people in 10 days after being released from prison.

During his murder trial in Douglas County, Jenkins was assessed by a doctor who concluded that he was ’a psychopath’ and ’one of the most dangerous people’ he had ever encountered.

Psychopath’: The 28-year-old, who a doctor described as ’one of the most dangerous people’ he had ever encountered, may use the botched case of self-mutilation as evidence he is mentally unstable .

Jenkins pleaded not guilty, then guilty, then ineligible for trial on the grounds of insanity. However, a judge dismissed the appeals and he was sentenced to life.

The decision of whether he would be sentenced to death was delayed after Jenkins revealed he had carved a swastika into his skin.

Following months of delays, he will face a panel in July to decide his fate.

It is believed Jenkins may use his latest botched case of self-mutilation as further evidence that he is mentally unstable.

## Justification

The information in the summary accurately represents the information in the source news article.

No, not fully attributable:. The summary contains any amount of information that is not supported by the source new article (including summaries that are only partially or not at all supported).

## Summary

saracens lost 13-9 to clermont at stade geoffroy-guichard on saturday . the sarries pack contained five english-qualified forwards . saracens ’ millionaire chairman nigel wray wants the salary cap scrapped .

## Original news article

saracens director of rugby mark mccall lauded his young guns after their latest european heartache before declaring he has no intention of overspending in a competitive post-world cup transfer market .

mccall watched his side , which contained five english-qualified forwards in the starting pack , battle in vain before losing 13-9 to the clermont on saturday .

saracens ’ millionaire chairman nigel wray spent much of last week repeating his belief the cap should be scrapped in order for saracens to compete at europe ’s top table , raising expectations they could be set to land a ‘ marquee ’ player from outside the league whose wages would sit outside next season ’s # 5.5 m cap.

However, with a series of upside-down 9s, Jenkins has fashioned himself an entirely unique - and irreversible - engraving.

maro itoje ( second left ) was one of five england-qualified forwards in the saracens pack that faced clermont mako vunipola tries to fend off clermont lock jamie cudmore during a ferocious contest saracens director of rugby mark mccall saw his side come agonisingly close to reaching the final but mccall said : ‘ we know where we ’d like to improve our side and we ’re prepared to wait for the right person . we do n’t want to jump in and get “ a name ” just because he ’s available post-world cup .

‘ the fact our pack is as young as it is is incredibly exciting for us . they could be the mainstay of the club for the next four to five seasons .

billy vunipola ( left ) , jim hamilton and itoje leave the field following their 13-9 loss against clermont

## Justification

The summary includes unattributed information: “at stade geoffroy-guichard”, and the reference to the opposing team as the “the sarries”, which is not supported in the original new article.

## Flag

There is a flag button in the bottom left corner of the task interface. Once flagged, you can proceed onto the next task. Use it to report tasks that are ineligible for reasons such as:

1. Missing components in the task.. Some tasks may have missing summaries or news articles. They should be flagged.

2. Malformed text.. Some text may be severely malformed with unintelligible artifacts (e.g. html code, unformatted tables, etc.). If any component of the task contains malformed text that makes it difficult for you to accomplish the task, the task should be flagged.

3. Source document is difficult to understand because it requires expert-level knowledge.. Some documents may include scientific formulas, obscure terminology, etc. If you can still understand enough of the document to rate the attributability, please do so. But, on the other hand, if properly evaluating the summary requires expertise in a particular area, please flag it.

## Appendix D: Evaluation Instructions for Table-to-Text

The following is a verbatim representation of the instructions that were presented to paid crowd annotators for performing the task alongside the interface. The prompts in the rating interface include wording from the instructions; the rating interface also contains hyperlinks to example sections in the instructions for each question and rating. The table-to-text instructions were developed after the conversational QA and summarization instructions had been established and the annotators had been trained on the conversation QA and summarization tasks.

## Overview

In this task you will evaluate the quality of a system-generated caption for highlighted parts of a table. The system is trying to convert the information in the table into a natural language description (what we are referring to as the “system-generated caption”). We want to rate the quality of the system-generated caption based on how well it represents information from the source table.

We will be using two categories to evaluate the quality of the caption: Interpretability and Attribution. You will evaluate these categories in succession. Some ratings will result in other categories being skipped. The task interface will guide you through the flow; you can also see the overall task flow in the diagram below.

![](images/957b77a51cf93956f586f3b14b45624643308ba094e891a7e70bf562dec3a557.jpg)

Note: The system-generated captions may appear very fluent and well-formed, but contain slight inaccuracies that are not easy to discern at first glance. Pay close attention to the text. Read it carefully as you would when proofreading.

The sections below describe each of the dimensions in detail. You can also flag ineligible tasks; the flagging criteria are described in this section.

## 1. Interpretability

In this step you will evaluate whether the system caption is interpretable by you.

You will be shown a system-generated caption of a table. Note that the table from which the caption is derived is hidden at this step, because we need to evaluate whether the caption is interpretable on its own. Carefully read the caption and answer the following question:

(Q1) Is all of the information relayed by the system caption interpretable to you?

This is asking whether you can understand the caption. If there is some part of the caption that is unclear or hard to interpret, select “No”. If prompted by the interface, enter a succinctly detailed justification of your rating.

Definition:. An uninterpretable caption has diminished intelligibility due to:

• Vague or ambiguous meaning, e.g., unclear noun references or insufficient context.

• Malformed phrases and sentences that are difficult to understand.

If the system caption is interpretable by you, you will proceed to the next category. In the section below, we show in more detail the kind of reasoning that should be used for establishing interpretability of captions. More examples of interpretability ratings and justifications are in this section of the appendix.

Interpreting the information provided in the system caption. Consider the following example:

## Caption

Mikhnevich and Avdeyeva both finished with 19.66 meters in the 2009 World Championships in Athletics – Women’s shot put.

In the above example, the meaning of the caption is clear even without seeing the source table. It is clear what the caption is reporting on and it stands on its own; that is, this caption is interpretable. It should be marked as “Yes, I understand it.” But consider another example:

## Caption

Mikhnevich and Avdeyeva finished with 19.66 metres.

In this case the meaning of the caption obviously depends on some context (“what did they finish?”), but that context is missing in the caption. Without additional information that clarifies that this is a result of a sports competition, the caption is difficult to interpret and it does not stand on its own. It should be marked as “No, the caption is unclear.”

Captions that require clarifications of this kind are one case where interpretability can be diminished. Other examples include nouns without a (clear) reference and malformed phrases and sentences:

## Caption 1

There are 87,814 Albanians, 624 Serbs and 361 Roma.

## Caption 2

J. Thomas Heflin (D) was a member until November 1, 1920 and William B. Bowling (D) succeeded him from December 14, 1920.

## Caption 3

George A. Gillett was a New Zealand dual-code international rugby

In caption 1, the numbers are missing the context of what they are being reported on (“what location or event do these numbers represent?”). In caption 2, the phrase “a member” lacks a specifying reference (“what was Thomas Heflin a member of?”). In caption 3, the sentence is difficult to understand as it appears to be missing a noun (“was George A. Gilet a rugby player?”).

In general, use your best judgment to determine the information provided by the caption. If you are unsure what the intended meaning of the caption is, err on the side of marking it with “No, the caption is unclear.”

## 2. Attribution

In this step, you will evaluate how well a system-generated caption is attributable to the source table. Note that the source table is a new element that will appear in the task only when you reach this question.

Note: We refer to “attributable to source table” interchangeably as “attribution” and “supported by the source table”. By which we mean, all of the information in the system caption can be verified from the source table.

You will be shown a system-generated caption. You will also be shown a table and its associated descriptions: title, section title and table section text. These elements provide additional context for understanding the information in the table. Finally, some cells in the table will be highlighted as helpful hints for which parts of the table are the focus of the caption. The table, descriptions and highlighted cells (source table) were used by the system to create the caption. You will use all of these elements to answer the following question:

(Q2) Is all of the information provided by the system caption fully supported by the source table?

This is asking whether all of the information in the system caption can be attributed to the information present in the source table. If prompted by the interface, enter a succinctly detailed justification of your rating.

Definition:. a fully supported (or attributable) system-generated caption contains an accurate representation of information in the source table. No information in the caption is unattested when compared against the source table and its associated descriptions (title, section title and table section text).

In the section below, we show in more detail the kind of reasoning that should be used for establishing attribution of captions. More examples of attribution ratings and justifications are in this section of the appendix.

Assessing the accuracy of the information in the caption against the source table. Again, you should use your best judgment in determining whether all of the information provided by the system caption is “an accurate representation of information in the source table”. We give the following guidance:

In determining this question, ask yourself whether it is accurate to say “the provided table says. . . ” or “according to the table. . . ” with the system caption following this phrase.

Be sure to check all of the information in the caption. If only some of the information is supported in the table, but other parts of the information are missing from the table or not an accurate representation, then please mark “No, not fully attributable.”

The concept of “accurate representation” should be close to a journalist’s conception of this phrase. For example take this excerpt from this page on Accuracy in the NPR Ethics Handbook: “When quoting or paraphrasing anyone. . . consider whether the source would agree with the interpretation. . . ” In other words, if you had written the source document, consider whether you would view the caption as an accurate representation of information in that source document.

## Some Final Important Notes.

Source quality.. When making your judgments in this template, do not take into account whether the underlying source table is correct or trustworthy. This is clearly important, but will be evaluated in a separate task. The “attribution” category is used only to judge whether the information provided by the system caption is an accurate representation of the underlying source table.

Highlighted cells.. Some of the cells in the table are highlighted. The highlighted cells are intended to be the focus of the caption, and can be used as a helpful hint of where to look in the table for information in the caption — though some captions may also refer to information from elsewhere in the table. If the caption does not capture the information in the highlighted cells, but otherwise accurately represents the information elsewhere in the table and its description, please still mark it “Yes, fully attributable.”

Examples of attribution ratings and justifications are in this section.

## Scoring and Examples

## Interpretability

No, the caption is unclear:. The caption is unclear and/or difficult to understand.

Caption Bradman scored 299.

The caption lacks sufficient context (“what did Bradman score in?”).

Caption

Amlogic Quad-core Cortex-A53, Mali-450 MP5 OpenGL ES 2.0, and H.264.

## Justification

The caption is malformed and difficult to interpret: the sentence appears to be missing a verb.

## Caption

The number one album of the year was Watch the Throne by Jay-Z and Kanye West, which sold 436,000 copies, and Lupe Fiasco’s Lasers, which sold 204,000 copies.

## Justification

The caption is malformed because it has two albums listed as “number one album of the year”. Additionally, “the year” lacks a reference (“what year was it?”).

## Attribution

Yes, fully attributable:. All the information in the caption is supported by the table and its description.

## Caption

The first-week sales of the album The Watch the Throne by Jay-Z and Kanye West sold 436,000 copies, while Lupe Fiasco’s Lasers sold 204,000 copies in the first week.

Source table

<table><tr><td colspan="6">2011 in hip hop music</td></tr><tr><td colspan="6">Section Title: Highest first-week salesTable Section Text: None</td></tr><tr><td>Number</td><td>Album</td><td>Artist</td><td>1st-week sales</td><td>1st-week position</td><td>Refs</td></tr><tr><td>1</td><td>Tha Carter IV</td><td>Lil Wayne</td><td>964,000</td><td>1</td><td></td></tr><tr><td>2</td><td>Take Care</td><td>Drake</td><td>631,000</td><td>1</td><td></td></tr><tr><td>3</td><td>Watch the Throne</td><td>Jay-Z &amp; Kanye West</td><td>436,000</td><td>1</td><td></td></tr><tr><td>4</td><td>Thug Motivation 103: Hustlerz Ambition</td><td>Young Jeezy</td><td>233,000</td><td>3</td><td></td></tr><tr><td>5</td><td>Cole World: The Sideline Story</td><td>J. Cole</td><td>217,000</td><td>1</td><td></td></tr><tr><td>6</td><td>Lasers</td><td>Lupe Fiasco</td><td>204,000</td><td>1</td><td></td></tr><tr><td>7</td><td>Rolling Papers</td><td>Wiz Khalifa</td><td>197,000</td><td>2</td><td></td></tr><tr><td>8</td><td>Hell: The Sequel</td><td>Bad Meets Evil</td><td>171,000</td><td>1</td><td></td></tr><tr><td>9</td><td>Ambition</td><td>Wale</td><td>164,000</td><td>2</td><td></td></tr><tr><td>10</td><td>Blue Slide Park</td><td>Mac Miller</td><td>144,000</td><td>1</td><td></td></tr></table>

## Justification

The information in the caption accurately represents the source table.

## Caption

Albanians are the largest ethnic group in Gjilan, followed by Serbs with 624 and Roma with 361 persons.

## Source table

<table><tr><td colspan="10">Gjilan</td></tr><tr><td colspan="10">Section Title: Ethnic groupsTable Section Text: The vast majority of the population is Albanian, followed by Serbs, and a small number of minorities. There are among others, 978 Turks or 1% of the municipal population.Ethnic composition</td></tr><tr><td>Year/population</td><td>Albanians</td><td>%</td><td>Serbs</td><td>%</td><td>Roma</td><td>%</td><td>Others</td><td>%</td><td>Total</td></tr><tr><td>1953</td><td>24,797</td><td>50.87</td><td>19,196</td><td>39.32</td><td></td><td></td><td></td><td></td><td>48,748</td></tr><tr><td>1961</td><td>29,942</td><td>57.12</td><td>18,297</td><td>34.91</td><td>735</td><td>1.50</td><td></td><td></td><td>52,415</td></tr><tr><td>1971</td><td>43,754</td><td>64.45</td><td>20,237</td><td>29.81</td><td>1,824</td><td>2.69</td><td></td><td></td><td>67,893</td></tr><tr><td>1981</td><td>59,764</td><td>71.08</td><td>19,212</td><td>22.85</td><td>3,347</td><td>3.98</td><td>1,762</td><td>2.1</td><td>84,085</td></tr><tr><td>1991</td><td>79,357</td><td>76.54</td><td>19,370</td><td>18.68</td><td>3,477</td><td>3.4</td><td>1,471</td><td>1.4</td><td>103,675</td></tr><tr><td>1998</td><td>94,218</td><td>79.4</td><td>19,481</td><td>16.4</td><td>3,568</td><td>3</td><td>1,387</td><td>1.2</td><td>118,654</td></tr><tr><td>2011</td><td>87,814</td><td>97,45</td><td>624</td><td>0,7</td><td>361</td><td>0,4</td><td>1,379</td><td>1,52</td><td>90,178</td></tr><tr><td colspan="10">Source: Yugoslav population censuses for data through 1991,and Kosovo 2011 census.</td></tr></table>

## Justification

The caption accurately reflects information from the source table. The fact that the Albanian ethnic group is the largest can be easily reasoned from the information in the table.

No, not fully attributable:. The caption cannot be fully attributed to the source table and its description (including captions that are only PARTIALLY or NOT AT ALL supported).

## Caption

The first-week sales of the album Watch the Throne by Jay-Z & Kanye West and Lupe Fiasco were 204,000 and the first-week sales of the album Lasers by Lupe Fiasco were 436,000.

Source table

<table><tr><td colspan="6">2011 in hip hop music</td></tr><tr><td colspan="6">Section Title: Highest first-week salesTable Section Text: None</td></tr><tr><td>Number</td><td>Album</td><td>Artist</td><td>1st-week sales</td><td>1st-week position</td><td>Refs</td></tr><tr><td>1</td><td>Tha Carter IV</td><td>Lil Wayne</td><td>964,000</td><td>1</td><td></td></tr><tr><td>2</td><td>Take Care</td><td>Drake</td><td>631,000</td><td>1</td><td></td></tr><tr><td>3</td><td>Watch the Throne</td><td>Jay-Z &amp; Kanye West</td><td>436,000</td><td>1</td><td></td></tr><tr><td>4</td><td>Thug Motivation 103: Hustlerz Ambition</td><td>Young Jeezy</td><td>233,000</td><td>3</td><td></td></tr><tr><td>5</td><td>Cole World: The Sideline Story</td><td>J. Cole</td><td>217,000</td><td>1</td><td></td></tr><tr><td>6</td><td>Lasers</td><td>Lupe Fiasco</td><td>204,000</td><td>1</td><td></td></tr><tr><td>7</td><td>Rolling Papers</td><td>Wiz Khalifa</td><td>197,000</td><td>2</td><td></td></tr><tr><td>8</td><td>Hell: The Sequel</td><td>Bad Meets Evil</td><td>171,000</td><td>1</td><td></td></tr><tr><td>9</td><td>Ambition</td><td>Wale</td><td>164,000</td><td>2</td><td></td></tr><tr><td>10</td><td>Blue Slide Park</td><td>Mac Miller</td><td>144,000</td><td>1</td><td></td></tr></table>

## Justification

The artists on the album Watch the Throne are only Jay-Z and Kanye West, excluding Lupe Fiasco. The first week’s sales of Watch the Throne were 436,000, not 204,000. The first week’s sales of Lasers were 204,000, not 436,000.

## Caption

Juan Mora Fernández was the Head of State of Costa Rica, winning 11 seats in the San José, 8 in Cartago, 8 in Heredia, 3 in Escazú , 2 in Ujarrás, 1 in Térraba and 1 in Bagaces.

Source table

![](images/37b10551b94c50b37cf4d2f8da8d7611177155d4a8f91c7a7abcf47d9179262b.jpg)

## Justification

The table does not have a clear identification of the reported numbers, while the caption identifies them as “seats”, which is not attributable anywhere in the table or its descriptions.

## Flag

There is a flag button in the bottom left corner of the task interface. Once flagged, you can proceed onto the next task. Use it to report tasks that are ineligible for reasons such as:

1. Missing components in the task.. Some tasks may have missing summaries or news articles. They should be flagged.

Note that table title, section title, or table section text could be empty or designated with “None”. These are acceptable and should not be flagged. See an example of an acceptable table description below:

## 1825 Costa Rican Head of State election

Section Title:

Table Section Text: None

2. Malformed text.. Some text may be severely malformed with unintelligible artifacts (e.g. html code, unformatted tables, etc.). If any component of the task contains malformed text, the task should be flagged.

## Caption

The lowest temperature recorded in Porto Alegre was ?? 0.3<sup>◦</sup>C (31.5<sup>◦</sup>F)

3. Source table is difficult to understand because it requires expert-level knowledge.. Some tables may include scientific formulas, obscure terminology, etc. If you can still understand enough of the table to rate its attributability, please do so. But if properly evaluating the response requires expertise in a particular area, please flag it.

The longest-lived isotope is 18mF with a half-life of 162 ns.

Source table

<table><tr><td colspan="9">Isotopes of fluorine</td></tr><tr><td colspan="9">Section Title: List of isotopesTable Section Text: Bold for stable isotopes Has medicinal uses</td></tr><tr><td>nuclide symbol</td><td>Z(p) excitation</td><td>N(n) energy</td><td>isotopic mass (u) half-life</td><td>decay mode(s)</td><td>daughter isotope(s)</td><td>nuclear spin and parity</td><td>representative isotopic composition (mole fraction)</td><td></td></tr><tr><td>14F</td><td>9</td><td>5</td><td>14.03432(4)</td><td>500(60)×10-24 s [910 keV]</td><td>p</td><td>13O</td><td>2-</td><td></td></tr><tr><td>15F</td><td>9</td><td>6</td><td>15.017785(15)</td><td>1.1(0.3)×10-21 s [1.0(2) MeV]</td><td>p</td><td>14O</td><td>1/2+</td><td></td></tr><tr><td>16F</td><td>9</td><td>7</td><td>16.011466(9)</td><td>11(6)×10-21 s [40(20) keV]</td><td>p</td><td>15O</td><td>0-</td><td></td></tr><tr><td>17F</td><td>9</td><td>8</td><td>17.00209524(27)</td><td>64.370(27) s</td><td>B+</td><td>17O</td><td>5/2+</td><td></td></tr><tr><td>18F</td><td>9</td><td>9</td><td>18.0009373(5)</td><td>109.739(9) min</td><td>B+ (96.86%)EC (3.14%)</td><td>18O18O</td><td>1+</td><td></td></tr><tr><td>18mF</td><td colspan="3">1121.36(15) keV</td><td>162(7) ns</td><td>IT</td><td>18F</td><td>5+</td><td></td></tr><tr><td>19F</td><td>9</td><td>10</td><td>18.9984031629(9)</td><td>Stable</td><td></td><td></td><td>1/2+</td><td>1.0000</td></tr><tr><td>20F</td><td>9</td><td>11</td><td>19.99998125(3)</td><td>11.163(8) s</td><td>B-</td><td>20Ne</td><td>2+</td><td></td></tr><tr><td>21F</td><td>9</td><td>12</td><td>20.9999489(19)</td><td>4.158(20) s</td><td>B-</td><td>21Ne</td><td>5/2+</td><td></td></tr><tr><td>22F</td><td>9</td><td>13</td><td>22.002999(13)</td><td>4.23(4) s</td><td>B- (89%)B-n (11%)</td><td>22Ne21Ne</td><td>(4+)</td><td></td></tr><tr><td>23F</td><td>9</td><td>14</td><td>23.00353(4)</td><td>2.23(14) s</td><td>B- (86%)B-n (14%)</td><td>23Ne22Ne</td><td>5/2+</td><td></td></tr><tr><td>24F</td><td>9</td><td>15</td><td>24.00810(10)</td><td>384(16) ms</td><td>B- (94.1%)B-n (5.9%)</td><td>24Ne23Ne</td><td>3+</td><td></td></tr><tr><td>25F</td><td>9</td><td>16</td><td>25.01217(10)</td><td>80(9) ms</td><td>B- (76.9%)B-n (23.1%)</td><td>25Ne24Ne</td><td>(5/2+)</td><td></td></tr><tr><td>26F</td><td>9</td><td>17</td><td>26.02002(12)</td><td>8.2(9) ms</td><td>B- (86.5%)B-n (13.5%)</td><td>26Ne25Ne</td><td>1+</td><td></td></tr><tr><td>26mF</td><td colspan="3">643.4(1) keV</td><td>2.2(1) ms</td><td>IT (82%)B-n (12%)B-n (6%)</td><td>26F25Ne26Ne</td><td>(4+)</td><td></td></tr><tr><td>27F</td><td>9</td><td>18</td><td>27.02732(42)</td><td>4.9(2) ms</td><td>B-, n (77%)B- (23%)</td><td>26Ne27Ne</td><td>5/2+#</td><td></td></tr><tr><td>28F</td><td>9</td><td>19</td><td>28.03622(42)</td><td>46×10-21 s</td><td>n</td><td>27F</td><td></td><td></td></tr><tr><td>29F</td><td>9</td><td>20</td><td>29.04310(56)</td><td>2.5(3) ms</td><td>B-, n (60%)B- (40%)</td><td>28Ne29Ne</td><td>5/2+#</td><td></td></tr><tr><td>31F</td><td>9</td><td>22</td><td>31.06027(59)#</td><td>1# ms [-260 ns]</td><td>B-</td><td>31Ne</td><td>5/2+#</td><td></td></tr></table>

## Justification

In order to be able to evaluate whether this table supports the caption, it requires a deeper understanding of scientific equations and terminology contained in the table. Because this example requires scientific expertise to evaluate it properly, it should be flagged.

## Appendix E: Annotator Interface for Conversational QA Tasks

In this task you will evaluate the quality of a system-generated response to a user query. The system is trying to help the user learn about a particular topic by answering their questions. Refer to the full instructions with rating examples

![](images/e22ba9540bb0b9b60395413acb9683d1d1ee5c614da2b09bc1d76eb93ceb4098.jpg)  
Figure 1

Interpretability stage. The source document is hidden. If the task is rated as not interpretable, the attribution stage is skipped and the annotator proceeds to the next task in the queue. During training and pilot, the justification element is shown only if the task is rated as not interpretable.

![](images/5deac78cb75d05eda03e5585c607a5f7497249972cb3596b0f0d813733837c79.jpg)  
Figure 2  
Attribution stage. The source document is shown. During training and pilot, the justification element is required for all ratings.

# Appendix F: Annotator Interface for Summarization Tasks

In this task you will evaluate the quality of a system-generated summary. The system's goal is to summarize the original source document, while remaining truthfu to it, Refer to the full instructions with rating examples

## Summary

The Leeds City Council elections were held on Thursday, 4 May 1995, with one third of the council up for election, alongside a vacancy in Roundhay. Labour won another victory over the opposition parties, winning a record number of wards as the Labour gains extended further into Conservative heartland.

1. Evaluate Interpretability 1. Evaluate Interpretability.

Is all of the information relayed by the system summary interpretable to you?Examole

Yes, I understand it. All of the information is clear and understandable

No. the summary is unclear. The summary is unclear and/or difficult to understand

Provide a justification for vour interpretability rating in 1. What makes the summary unclear and/or hard to interpret? Examples

Flag

## Figure 1

Interpretability stage. The source document is hidden. If the task is rated as not interpretable, the attribution stage is skipped and the annotator proceeds to the next task in the queue. During training and pilot, the justification element is shown only if the task is rated as not interpretable.

In this task vou will evaluate the quality of a system-generated summary. The system's goal is to summarize the original source document, while remaining truthful to it. Refer to the full instructions with rating examples.

## Summary

The Leeds City Council elections were held on Thursday, 4 May 1995, with one third of the council up for election, alongside a vacancy in Roundhay. Labour won another victory over the opposition parties, winning a record number of wards as the Labour gains extended further into Conservative heartland

1. Evaluate Interpretability. 1. Evaluate Interpretability.

Is all of the information relayed by the system summary interpretable to you? Example

Yes, Iunderstand it, All of the information is clear and understandable.

No the summary is unclear The summary is unclear and/or ditficult to understand

2. Evaluate Attribution. Is all of the information provided by the system summary fully attributable to the source document?

Yes, fully attributable, All the information in the system summary is supported by the document. Examples

No, pot fully attriburtable. The system summany cannot be fully attributed to the document. Examples

Provide a justification for your attribution rating in 2. What parts of the summary are and are not supported by the source document? Example

## Source document

The Leeds City Council elections were held on Thursday, 4 May 1995, with one third of the council up for election, alongside a vacancy in Roundhay.

Labour won another victory over the oppositior parties, winning a record number of wards as the Labour gains extended further into Conseryative heartland A disastrous result for the Tories saw them fall even further from the record lows they set the year before, losing Cookridge, North and Roundhay for the first time - with Wetherby their sole defence. Labour gained eight in total, securing second councillors in the previously reliable Conservative wards of Aireborough, Halton, Pudsey North and Weetwood, As a result, Labour represented over three-quarters of the council with a formidable majority of 51

P Flag

## Figure 2

Attribution stage. The source document is shown. During training and pilot, the justification element is required for all ratings.

In this task you will evaluate the quality of a system-generated sentence. The system's goal is to transform the highlighted cells of the data into a natural language sentence, while remaining truthful to the table and its description. Refer to the full instructions with rating examples

![](images/0a406e9b47439cb5510e83bbc5dd099f6d73e2e07f76f79f067e67032ac3dbc3.jpg)  
Figure 2  
Attribution stage. The source table its description are shown. The rendering preserves highlighted cells from the ToTTo data. During training and pilot, the justification element is shown for all ratings in the second stage.

## Acknowledgments

The authors would like to thank Roee Aharoni, Sebastian Gehrmann, Mirella Lapata, Hongrae Lee, Shashi Narayan, Ankur Parikh, Fernando Pereira, and Idan Szpektor for their detailed feedback on the manuscript and throughout the project. We would also like to thank Ashwin Kakarla and his team for making the human evaluation study possible and Alejandra Molina and Kristen Olson for their guidance on the task interface design. We are thankful to the larger Google Research community for the many discussions during the course of this project.

## References

Adiwardana, Daniel, Minh-Thang Luong, David R So, Jamie Hall, Noah Fiedel, Romal Thoppilan, Zi Yang, Apoorv Kulshreshtha, Gaurav Nemade, Yifeng Lu, et al. 2020. Towards a human-like open-domain chatbot. arXiv preprint arXiv:2001.09977.

Anantha, Raviteja, Svitlana Vakulenko, Zhucheng Tu, Shayne Longpre, Stephen Pulman, and Srinivas Chappidi. 2021. Open-domain question answering goes conversational via question rewriting. In Proceedings of NAACL.

Belz, Anja, Simon Mille, and David M Howcroft. 2020. Disentangling the properties of human evaluation methods: A classification system to support comparability, meta-evaluation and reproducibility testing. In Proceedings of the 13th International Conference on Natural Language Generation, pages 183–194.

Carston, Robyn. 1988. Implicature, explicature, and truth-theoretic semantics. In Ruth Kempson, editor, Mental Representations: The Interface Between Language and Reality. Cambridge University Press, pages 155–181.

Choi, Eunsol, He He, Mohit Iyyer, Mark Yatskar, Wen-tau Yih, Yejin Choi, Percy Liang, and Luke Zettlemoyer. 2018. QuAC: Question answering in context. In Proceedings of EMNLP.

Choi, Eunsol, Jennimaria Palomaki, Matthew Lamm, Tom Kwiatkowski, Dipanjan Das, and Michael Collins. 2021. Decontextualization: Making Sentences Stand-Alone. Transactions of the Association for Computational Linguistics, 9:447–461.

Dalton, Jeffrey, Chenyan Xiong, Vaibhav Kumar, and Jamie Callan. 2020. Cast-19: A dataset for conversational information

seeking. Proceedings of SIGIR.

Dinan, Emily, Stephen Roller, Kurt Shuster, Angela Fan, Michael Auli, and Jason Weston. 2019. Wizard of wikipedia: Knowledge-powered conversational agents. In Proceedings of ICLR.

Durmus, Esin, He He, and Mona Diab. 2020. FEQA: A question answering evaluation framework for faithfulness assessment in abstractive summarization. In Proceedings of ACL.

Dziri, Nouha, Hannah Rashkin, Tal Linzen, and David Reitter. 2021. Evaluating groundedness in dialogue systems: The BEGIN benchmark. ArXiv, abs/2105.00071.

Gehrmann, Sebastian, Tosin Adewumi, Karmanya Aggarwal, Pawan Sasanka Ammanamanchi, Anuoluwapo Aremu, Antoine Bosselut, Khyathi Raghavi Chandu, Miruna-Adriana Clinciu, Dipanjan Das, Kaustubh Dhole, Wanyu Du, Esin Durmus, Ondˇrej Dušek, Chris Chinenye Emezue, Varun Gangal, Cristina Garbacea, Tatsunori Hashimoto, Yufang Hou, Yacine Jernite, Harsh Jhamtani, Yangfeng Ji, Shailza Jolly, Mihir Kale, Dhruv Kumar, Faisal Ladhak, Aman Madaan, Mounica Maddela, Khyati Mahajan, Saad Mahamood, Bodhisattwa Prasad Majumder, Pedro Henrique Martins, Angelina McMillan-Major, Simon Mille, Emiel van Miltenburg, Moin Nadeem, Shashi Narayan, Vitaly Nikolaev, Andre Niyongabo Rubungo, Salomey Osei, Ankur Parikh, Laura Perez-Beltrachini, Niranjan Ramesh Rao, Vikas Raunak, Juan Diego Rodriguez, Sashank Santhanam, João Sedoc, Thibault Sellam, Samira Shaikh, Anastasia Shimorina, Marco Antonio Sobrevilla Cabezudo, Hendrik Strobelt, Nishant Subramani, Wei Xu, Diyi Yang, Akhila Yerukola, and Jiawei Zhou. 2021. The GEM benchmark: Natural language generation, its evaluation and metrics. In Proceedings of the 1st Workshop on Natural Language Generation, Evaluation, and Metrics.

Gopnik, Alison and Henry M. Wellman. 1992. Why the child’s theory of mind really is a theory. Mind & Language, 7(1-2):145–171.

Grice, Herbert P. 1975. Logic and conversation. In Speech acts. Brill, pages 41–58.

Gupta, Prakhar, Chien-Sheng Wu, Wenhao Liu, and Caiming Xiong. 2021. Dialfact: A benchmark for fact-checking in dialogue.

ArXiv, abs/2110.08222.

Harrington, Leo A, Michael D Morley, A Šcedrov, and Stephen G Simpson. 1985. Harvey Friedman’s research on the foundations of mathematics. Elsevier.

Honovich, Or, Leshem Choshen, Roee Aharoni, Ella Neeman, Idan Szpektor, and Omri Abend. 2021. q<sup>2</sup>: Evaluating factual consistency in knowledge-grounded dialogues via question generation and question answering. In Proceedings of EMNLP.

Howcroft, David M, Anja Belz, Miruna-Adriana Clinciu, Dimitra Gkatzia, Sadid A Hasan, Saad Mahamood, Simon Mille, Emiel van Miltenburg, Sashank Santhanam, and Verena Rieser. 2020. Twenty years of confusion in human evaluation: Nlg needs evaluation sheets and standardised definitions. In Proceedings of the 13th International Conference on Natural Language Generation, pages 169–182.

Kwiatkowski, Tom, Jennimaria Palomaki, Olivia Redfield, Michael Collins, Ankur Parikh, Chris Alberti, Danielle Epstein, Illia Polosukhin, Jacob Devlin, Kenton Lee, Kristina Toutanova, Llion Jones, Matthew Kelcey, Ming-Wei Chang, Andrew M. Dai, Jakob Uszkoreit, Quoc Le, and Slav Petrov. 2019. Natural questions: A benchmark for question answering research. Transactions of the Association for Computational Linguistics, 7:452–466.

Ladhak, Faisal, Esin Durmus, He He, Claire Cardie, and Kathleen McKeown. 2022. Faithful or extractive? on mitigating the faithfulness-abstractiveness trade-off in abstractive summarization. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 1410–1421, Association for Computational Linguistics, Dublin, Ireland.

Maynez, Joshua, Shashi Narayan, Bernd Bohnet, and Ryan McDonald. 2020. On faithfulness and factuality in abstractive summarization. In Proceedings of ACL.

Mehri, Shikib and Maxine Eskenazi. 2020. USR: An unsupervised and reference free evaluation metric for dialog generation. In Proceedings of ACL, Online.

Nallapati, Ramesh, Bowen Zhou, Cicero dos Santos, Ça ˘glar Gulçehre, and Bing Xiang.˙ 2016. Abstractive text summarization using sequence-to-sequence RNNs and beyond. In Proceedings of CoNLL.

Nan, Feng, Cicero Nogueira dos Santos, Henghui Zhu, Patrick Ng, Kathleen

McKeown, Ramesh Nallapati, Dejiao Zhang, Zhiguo Wang, Andrew O. Arnold, and Bing Xiang. 2021. Improving factual consistency of abstractive summarization via question answering. In Proceedings of ACL.

Nie, Yixin, Haonan Chen, and Mohit Bansal. 2019. Combining fact extraction and verification with neural semantic matching networks. In Proceedings of AAAI.

Parikh, Ankur, Xuezhi Wang, Sebastian Gehrmann, Manaal Faruqui, Bhuwan Dhingra, Diyi Yang, and Dipanjan Das. 2020. ToTTo: A controlled table-to-text generation dataset. In Proceedings of EMNLP.

Pavlick, Ellie and Tom Kwiatkowski. 2019. Inherent Disagreements in Human Textual Inferences. Transactions of the Association for Computational Linguistics, 7:677–694.

Raffel, Colin, Noam Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei Li, and Peter J. Liu. 2020. Exploring the limits of transfer learning with a unified text-to-text transformer. Journal of Machine Learning Research, 21:140:1–140:67.

Rashkin, Hannah, David Reitter, Gaurav Singh Tomar, and Dipanjan Das. 2021. Increasing faithfulness in knowledge-grounded dialogue with controllable features. In Proceedings of ACL.

Ribeiro, Marco Tulio, Sameer Singh, and Carlos Guestrin. 2016. Model-agnostic interpretability of machine learning. arXiv preprint arXiv:1606.05386.

Santhanam, Sashank, Behnam Hedayatnia, Spandana Gella, Aishwarya Padmakumar, Seokhwan Kim, Yang Liu, and Dilek Hakkani-Tur. 2021. Rome was built in 1776: A case study on factual correctness in knowledge-grounded response generation. arXiv preprint arXiv:2110.05456.

See, Abigail, Peter J. Liu, and Christopher D. Manning. 2017. Get to the point: Summarization with pointer-generator networks. In Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 1073–1083, Association for Computational Linguistics, Vancouver, Canada.

Shuster, Kurt, Da Ju, Stephen Roller, Emily Dinan, Y-Lan Boureau, and Jason Weston. 2020. The dialogue dodecathlon: Open-domain knowledge and image grounded conversational agents. In

Proceedings of ACL.

Thorne, James, Max Glockner, Gisela Vallejo, Andreas Vlachos, and Iryna Gurevych. 2021. Evidence-based verification for real world information needs. CoRR, abs/2104.00640.

Thorne, James and Andreas Vlachos. 2018. Automated fact checking: Task formulations, methods and future directions. In Proceedings of COLING.

Thorne, James, Andreas Vlachos, Christos Christodoulopoulos, and Arpit Mittal. 2018. FEVER: a large-scale dataset for fact extraction and VERification. In Proceedings of NAACL.

Wang, Alex, Kyunghyun Cho, and Mike Lewis. 2020. Asking and answering questions to evaluate the factual consistency of summaries. In Proceedings of ACL.

Welleck, Sean, Jason Weston, Arthur D. Szlam, and Kyunghyun Cho. 2019. Dialogue natural language inference. In Proceedings of ACL.

Wilson, Deirdre and Dan Sperber. 2004. Relevance Theory, The Handbook of Pragmatics. Blackwell.

Wiseman, Sam, Stuart Shieber, and Alexander Rush. 2017. Challenges in data-to-document generation. In Proceedings of EMNLP.

Zaheer, Manzil, Guru Guruganesh, Kumar Avinava Dubey, Joshua Ainslie, Chris Alberti, Santiago Ontanon, Philip Pham, Anirudh Ravula, Qifan Wang, Li Yang, and Amr Ahmed. 2020. Big bird: Transformers for longer sequences. In Advances in Neural Information Processing Systems, volume 33, pages 17283–17297, Curran Associates, Inc.

Zhong, Ming, Pengfei Liu, Yiran Chen, Danqing Wang, Xipeng Qiu, and Xuanjing Huang. 2020. Extractive summarization as text matching. In Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics, pages 6197–6208, Association for Computational Linguistics, Online.