# EpLSA
### Installing
 ```
transformers==3.3.1
torch==1.7.0
nltk==3.4.5
networkx==2.1
spacy==2.2.1
psutil==5.9.0

```
 
Training
The optimal parameters are provided in the script
Training anlg dataset
```
bash  scripts/train_anlg.sh
```
Training eg dataset
```
bash  scripts/train_eg.sh
```
Training seg dataset
```
bash  scripts/train_seg.sh
```
We will provide our trained checkpoints.

Inference

```
bash  scripts/predict.sh
```
**Case Study**
We provide some test cases on three dataset.

| **Abductive Commonsense Reasoning**                          |
| ------------------------------------------------------------ |
| O1: I wanted some cabinets to put in my bedroom.<br/>O2: After two months of work I had crafted some beautiful cabinets ! |
| **MoE: (Shen et al., 2019)**                                 |
| (1) I went to the store to look for cabinets.<br/>(2) I went to the store to look for some.<br/>(3) I found some beautiful maple cabinets online and purchased them. |
| **Nucleus sampling: (Holtzman et al., 2020)**                |
| (1) I went to the store and bought cabinets.<br/>(2) I went to the store and bought some materials.<br/>(3) I went to the store and bought some materials. |
| **MoKGE: (Yu et al., 2022)**                                 |
| (1) I looked online for some cabinets. I buy some.<br/>(2) So I went to the store and purchased some new and beautiful cabinets.<br/>(3) I decided to put together some beautiful cabinets for my bedroom. |
| **EpLSA (Ours)**                                             |
| (1) I decided to hire a professional to make them.<br/>(2) I found some that I liked and decided to make them.<br/>(3) I spent a lot of time on to the store to look at different cabinets |





| Story Ending Generation                                      |
| ------------------------------------------------------------ |
| Statement:<br/>Juan was driving at night when he saw a shooting star.<br/>He stopped his car to look at the sky.<br/>Many more came and went before his eyes.<br/>He had been so depressed, the sight elated him. |
| **MoE: (Shen et al., 2019)**                                 |
| (1) Juan decided to take a trip to see more shooting stars in the future.<br/>(2) Juan decided to take a trip to the local zoo.<br/>(3) He decided to take a trip to see more shooting stars in the future. |
| **Nucleus sampling: (Holtzman et al., 2020)**                |
| (1) Juan decided to take a trip to the movies in the future.<br/>(2) Juan decided he would become a shooting star painter.<br/>(3) He decided to take a trip to the movies one day . |
| **MoKGE: (Yu et al., 2022)**                                 |
| (1) Juan decided to go home and take a long look at the stars.<br/>(2) Then he realized it was just another day and went home.<br/>(3) He took a deep breath and went back to reality. |
| **EpLSA (Ours)**                                             |
| (1) Juan drove off into the night sky happy and content.<br/>(2) He drove away feeling proud of himself for seeing such a sight.<br/>(3) Juan was glad he had decided to watch shooting stars. |


| Explanation Generation                                       |
| ------------------------------------------------------------ |
| Statement: Marry lit up rocks to make a campfire.            |
| **MoE: (Shen et al., 2019)**                                 |
| (1) Rocks are too heavy to make a campfire.<br/>(2) Rocks are not flammable and can’t be lit.<br/>(3) Rocks are not flammable and cannot be lit. |
| **Nucleus sampling: (Holtzman et al., 2020)**                |
| (1) Rocks are too hard to make a campfire.<br/>(2) Rocks are too hard to make a campfire.<br/>(3) Rocks are too hard to make a campfire. |
| **MoKGE: (Yu et al., 2022)**                                 |
| (1) Rocks are not flammable and can’t be lit.<br/>(2) You don’t make campfires with fire, you make fire with fire.<br/>(3) fire is used to make fire not to make campfire. |
| **EpLSA (Ours)**                                             |
| (1) Rocks don’t catch fire, so they can’t be used to make fire.<br/>(2) fire can not be lit up rocks, not burnt them.<br/>(3) Rocks don’t catch fire and would not make a campfire. |
