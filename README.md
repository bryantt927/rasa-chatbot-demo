## Japanese Chatbot for Language Learners using [Rasa](https://rasa.com/)

#### This is a simple chatbot aimed to help beginner Japanese language learners practice a basic conversation.

#### Installing Rasa: Follow these instructions to download [Rasa](https://rasa.com/) for:
* [Windows](https://learning.rasa.com/installation/)
* [MacOS](https://learning.rasa.com/installation/mac/)
* [Ubuntu](https://learning.rasa.com/installation/ubuntu/)

#### Install the Spacy Model
Run `python -m spacy download ja_core_news_lg` to download the [Spacy Model](https://spacy.io/models/ja#ja_core_news_lg) that the bot uses.

#### Running The Bot In The Shell
To run the bot in the shell, change directory to the folder that the project is in and type the command `rasa shell` or `rasa shell --debug` and simultaneously in a separate shell window, run `rasa run actions` .
###### `rasa shell`
![image](https://user-images.githubusercontent.com/76408777/203106974-c793804d-16c6-4885-85c7-6ebce5b9918d.png)

###### `rasa run actions`
![Screenshot from 2022-11-21 11-23-22](https://user-images.githubusercontent.com/76408777/203106452-e9c4b030-0823-4756-93b3-5228e968614f.png)

When the bot loads, type `こんにちは` to start the conversation!
![image](https://user-images.githubusercontent.com/76408777/203107584-bbffe89b-5f56-445b-93ce-63207129589a.png)

#### Stopping The Bot In The Shell
Type `/stop` to exit the bot in the shell.

![image](https://user-images.githubusercontent.com/76408777/203108052-0e62ac4b-940b-4fea-8912-a23af19e6367.png)
