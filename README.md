# CEPC
This is the README file for our constructed dataset contained in "data_final.txt".

The file contains 2085 documents, each of which contains one emotion-cause pair (ECP), with one emotion clause and at most three cause clauses.
The document is annotated as follows:

`````````````````````````````````````````````````````````````````````````````````
doc_index doc_length doc_type
(emotion_clause_index, cause_clause_index), ...
clause_index, clause_type, emotion_type, emotion_word, clause content
...
`````````````````````````````````````````````````````````````````````````````````

doc_index: the index of the document;

doc_length: the number of clauses in this document;

doc_type: the type of the document,
    - 0: Not-causal; there is No causal relationship in this document since it contains a conditional ECP but the context information needed is missing;
    - 1: Conditional; the document contains a conditional ECP and the context information needed is included;
    - 2: Others; the document contains a non-conditional ECP;

emotion_clause_index: the index of the emotion clause;

cause_clause_index: the index of the cause clause;

clause_index: the index of the clause;

clause_type: the type of the clause,
    - 0: Irrelevant context clause (IR);
    - 1: Cause-Related context clause (CR);
    - 2: Emotion-Related context clause (ER);
    - 3: ECP-Related context clause (PR);
    - 4: Cause clause (C);
    - 5: Emotion clause (E);
    - 9: Both-Cause-and-Emotion clause (B);

emotion_type: the type of the emotion expressed in the clause:
    - Happiness, Sadness, Angry, Surprise, Disgust, Fear

emotion_word: the word expressing the emotion

clause content: the content of the clause
