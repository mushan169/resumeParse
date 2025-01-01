import os
import pandas as pd
import spacy
import random
import joblib
from spacy.training.example import Example
import time


def GroupData(content,label,TRAIN_DATA):
    for line in range(len(content)):
        Entity = {}
        Entities = []
        for i in eval(label[line]):
            if 'int' in str(type(i)):
                Entities.append(eval(label[line]))
                break
            if 'tuple' in str(type(i)):
                Entities.append(i)
        Entity["entities"] = Entities
        TRAIN_DATA.append((content[line],Entity))
    return TRAIN_DATA

def train_spacy(TRAIN_DATA, iterations):
    # 创建一个空白英文模型：en，中文模型:zh
    nlp = spacy.blank("en")
    #若没有则添加NER组件
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner",last=True)
    #添加所有实体标签到spaCy模型
    for _, annotations in TRAIN_DATA:
        # print(annotations.get("entities"))
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    #获取模型中除了NER之外的其他管件
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    #开始训练   #消除其他管件的影响
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
        optimizer.learn_rate = 1e-3
        for itn in range(iterations):
            print("开始迭代",itn + 1,"次")
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                try:
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annotations)
                    nlp.update([example], losses=losses, sgd=optimizer)    # drop=0.4
                except:
                    continue
    return (nlp)

