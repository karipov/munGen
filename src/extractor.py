import copy
import os
import re
import glob
import pprint
from random import shuffle
from concurrent.futures import ProcessPoolExecutor, as_completed

from IPython.display import clear_output
import pandas as pd
import pdfplumber
import nltk


# clauses starters, taken from https://www.un.org/en/model-united-nations/drafting-resolutions
PREAMBS = [
    'Reiterating', 'Recognizing', 'Highlighting', 'Acknowledging', 'Affirming', 'Appreciating', 'Approving', 'Aware', 'Bearing in mind', 'Believing', 
    'Convinced', 'Desiring', 'Disturbed', 'Emphasizing', 'Expecting', 'Expressing', 'Fully', 'Guided', 'Having', 'Mindful', 'Noting', 'Emphasising'
    'Observing', 'Reaffirming', 'Realising', 'Realizing', 'Recalling', 'Recognising', 'Seeking', 'Underlining', 'Welcoming', 'Whereas',
    'Deeply alarmed', 'Alarmed', 'Stressing', 'Taking', 'Deeply', 'Cognizant', 'Appreciative', 'Confident', 'Congratulating', 'Recognizing'
    'Declaring', 'Deploring', 'Fulfilling', 'Keeping', 'Pointing', 'Referring', 'Reminding', 'Viewing', 'Commending', 'Concerned', 'Conscious', 'Considering'
]
OPERS = [
    'Also requests', 'Welcomes', 'Accepts', 'Adopts', 'Agrees', 'Appeals', 'Approves', 'Authorizes', 'Commends', 'Condemns', 'Considers', 'Decides', 'Declares', 'Determines',
    'Also decides', 'Directs', 'Emphasizes', 'Encourages', 'Endorses', 'Invites', 'Notes', 'Notes with approval', 'Notes with concern', 'Notes with satisfaction', 'Proclaims', 'Calls',
    'Reaffirms', 'Recommends', 'Reminds', 'Repeals', 'Requests', 'Resolves', 'Suggests', 'Stresses', 'Supports', 'Takes note', 'Urges', 'Expresses', 'Further', 'Also', 'Acknowledges',
    'Recognizes', 'Reiterates', 'Affirms', 'Asks', 'Authorises', 'Congratulates', 'Confirms', 'Deplores', 'Designates', 'Hopes', 'Proposes', 'Regrets', 'Seeks', 'Strongly', 'Trusts', 'Transmits'
]


def process_files(file):
    """ Processing and regex for files in an async manner """
    results = list()

    with pdfplumber.open(file) as pdf:

        all_clauses = list()
        all_text = str()

        for page in pdf.pages:
            text = page.extract_text()

            if not text:
                continue

            all_text += text

            # text cleaning
            text = re.sub(' +', ' ', re.sub(r'\t|\n|\r', ' ', text)).strip()  # cleaning multiple spaces and indentation chars
            text = re.sub('(\s+)', ' ', re.sub('[^a-z\s]+', ' ', text, flags=re.IGNORECASE)).strip()  # removing everything not in the english alphabet

            clauses = re.split(f"({'|'.join(PREAMBS + OPERS)})", text)  # split by preambular and operative clauses, keeping delimeter
            clauses = [a + ' ' + b for a, b in zip(clauses[1::2],  clauses[::2])] # connecting split delimeters and their clauses
            clauses = [re.sub(r'[A-Z]+[\s]+', ' ', x) for x in clauses] # cleaning independent leftover debris characters
            clauses = [re.sub(' +', ' ', x) for x in clauses]  # once more cleaning multiple spaces and indentation chars
            clauses = [x for x in clauses if not bool(re.findall(r'\w{20,}', x))]  # removes words 20 chars or more
            clauses = [x for x in clauses if len(x.split()) > 10]  # any clauses with less than 10 words

            all_clauses.extend(clauses[2:-1]) # removing the end and beginning elements because of headers & footers

    # exit if no text extraction has been made
    if not all_text:
        return None

    # extracting resolution name
    names = re.findall(r'A\/RES\/\d{2}\/\d{1,3}', all_text)
    names = list(set(names))
    name = str()

    if len(names) == 1:
        name = names[0]
    # elif len(names) > 1 and len(all_clauses) > 0:
    #     print('[ACTION]: multiple res symbols:', names, 'choose index; file', file)
    #     index = int(input('>>> '))
    #     name = names[index]
    else:
        return None

    # adding information for dataframe
    for clause in all_clauses:
        results.append([name, clause])

    return results

    # logging and such:
    # print(f"PROG: {i}/{len(files)} ({round(i / len(files) * 100, 2)}%); added {len(all_clauses)} clauses from {name} ({file}) to dataframe.")
    # counter += 1

    # if counter % 20 == 0:
    #     clear_output(wait=True)


def main():
    files = glob.glob("files/pdf/*"); shuffle(files);
    all_data = list()
    counter = 0

    with ProcessPoolExecutor() as executor:
        bunch_of_futures = {executor.submit(process_files, file): file for file in files}

        for i, future in enumerate(as_completed(bunch_of_futures)):
            try:
                data = future.result()
            except Exception as e:
                print(e)

            if not data:
                continue
            else:
                counter += 1

            len_clauses = len(data)
            name = data[0][0]
            file = bunch_of_futures[future]
            all_data.extend(data)

            print(f"PROG: {i}/{len(files)} ({round(i / len(files) * 100, 2)}%); added {len_clauses} clauses from {name} ({file}) to dataframe.")

            # if counter % 20 == 0:
            #     print(f"CURRENT PROGRESS: {round(i / len(files) * 100, 2)}\n"

    df = pd.DataFrame(all_data, columns=['resolution', 'clause'])
    df.to_csv("files/un_resos.csv")

if __name__ == "__main__":
    main()