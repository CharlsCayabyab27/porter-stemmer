import re
import csv
import pandas as pd
import multiprocessing
import sys

class PorterStemmer:
    def __init__(self) -> None:
        self.vowels = 'aeiou'

    def is_consonant(self, word, i):
        if word[i] not in self.vowels:
            if word[i] == 'y':
                if i == 0:
                    return True
                else:
                    return not self.is_consonant(word, i - 1)
            return True
        return False

    def is_vowel(self, word, i):
        if word[i] in self.vowels:
            return True
        else:
            return False

    def m_count(self, word):
        vc_pair = re.compile(f'{self.is_vowel}(?:{self.is_consonant})+')
        pairs = vc_pair.findall(word)
        return len(pairs)

    def has_vowel(self, word):
        if word.endswith('ing'):
            word = word[:-3]
            if any(vowel in word for vowel in ['a', 'e', 'i', 'o', 'u']):
                return True
                
        elif word.endswith('ed'):
            word = word[:-2]
            if any(vowel in word for vowel in ['a', 'e', 'i', 'o', 'u']):
                return True
        return False


    def end_with_cvc(self, word):
        if len(word) >= 3:
            if not self.is_consonant(word, -3) and self.is_consonant(word, -2) and not self.is_consonant(word, -1):
                return True
        return False


    def step1a(self, word):
        if word.endswith('sses'):
            return word[:-2]
        elif word.endswith('ies'):
            return word[:-2]
        elif word.endswith('ss'):
            return word
        elif word.endswith('s'):
            return word[:-1]
        return word

    def step1b(self, word):
        m = PorterStemmer.m_count(self, word)
        flag = False
        if word.endswith('eed') and m > 0:
            return word[:-1]
        elif word.endswith('ed') and self.has_vowel(word):
            return word[:-2]
            flag = True
        elif word.endswith('ing') and self.has_vowel(word):
            return word
            flag = True
        if flag:
            if word.endswith('at') or word.endswith('bl') or word.endswith('iz'):
                return word + 'e'
            elif word.endswith('s'):
                return word[:-1]
            elif self.end_with_cvc(word) and m == 1:
                return word
            elif word[-1] == word[-2] and word[-1] not in ('L', 'S', 'Z'):
                return word[:-1]
            else:
                return word
        return word

    def step1c(self, word):
        if word.endswith('y'):
            if re.search('[aeiouy]', word[:-1]):
                return word[:-1] + 'i'
        return word

    def step2(self, word):
        m = PorterStemmer.m_count(self, word)
        if word.endswith('ational') and m > 0:
            return word[:-7] + 'ate'
        elif word.endswith('tional') or word.endswith('ousli') or word.endswith('entli') or word.endswith('eli') and m > 0:
            return word[:-2]
        elif word.endswith('enci') or word.endswith('anci') or word.endswith('abli') and m > 0:
            return word[:-1] + 'e'
        elif word.endswith('izer') and m > 0:
            return word[:-1]
        elif word.endswith('alli') and m > 0:
            return word[:-2]
        elif word.endswith('ization') and m > 0:
            return word[:-5] + 'e'
        elif word.endswith('ation') or word.endswith('iviti') and m > 0:
            return word[:-3] + 'e'
        elif word.endswith('ator') and m > 0:
            return word[:-2] + 'te'
        elif word.endswith('alism') or word.endswith('aliti') and m > 0:
            return word[:-3]
        elif word.endswith('iveness') and m > 0:
            return word[:-5]
        elif word.endswith('fulness') or  word.endswith('ousness') and m > 0:
            return word[:-4]
        elif word.endswith('biliti') and m > 0:
            return word[:-5] + 'le'
        return word

    def step3(self, word):
        m = PorterStemmer.m_count(self, word)
        if m > 0 and word.endswith('icate') or word.endswith('alize') or word.endswith('iciti'):
            return word[:-3]
        elif m > 0 and word.endswith('ative'):
           return word
        elif m > 0 and word.endswith('ical'):
            return word[:-2]
        elif m > 0 and word.endswith('ful') or word.endswith('ness'):
            return word
        return word

    def step4(self, word):
        m = PorterStemmer.m_count(self, word)
        suffixes = ['al', 'ance', 'ence', 'er', 'ic', 'able', 'ible', 'ant', 'ement',
                   'ment', 'ou', 'ism', 'ate', 'iti', 'ous', 'ive', 'ize']
        if m > 1 and any(word.endswith(suffix) for suffix in suffixes):
            return word
        elif m > 1 and word.endswith('sion') or word.endswith('tion'):
            return word[:-3]
        return word

    def step5a(self, word):
        m = PorterStemmer.m_count(self, word)
        if m > 1 and word.endswith('e'):
            return word
        elif m == 1 and word.endswith('es') and not PorterStemmer.end_with_cvc(word):
            return word
        return word

    def step5b(self, word):
        m = PorterStemmer.m_count(self, word)
        if m > 1 and word.endswith('ll') or word.endswith('dd'):
            return word[:-1]
        return word



    def stem_word(self, word):
        if len(word) < 3:
            return word
        else:
            word = self.step1a(word)
            word = self.step1b(word)
            word = self.step1c(word)
            word = self.step2(word)
            word = self.step3(word)
            word = self.step4(word)
            word = self.step5a(word)
            word = self.step5b(word)
        return word

def stem_cell(cell):
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem_word(token) for token in cell.split()]
    return ' '.join(stemmed_tokens)


def process_chunk(chunk):
    return chunk.map(lambda cell: stem_cell(cell) if pd.notna(cell) else '')

if __name__ == "__main__":
    try:
        input_file_path = '4-cols_15k-rows.csv-4-cols_15k-rows.csv.csv'
        output_file_path = "stemmesd-dataset_15k_rows_cayabyab-charls.csv"

        # Read the input CSV file using pandas
        df = pd.read_csv(input_file_path)

        # Configure multiprocessing
        num_cores = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=num_cores)

        # Split the DataFrame into chunks for parallel processing
        chunk_size = len(df) // num_cores
        if chunk_size > 0:
            df_chunks = [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
        else:
            print("Invalid chunk size. Please check your input data.")
            sys.exit(1)
            
        # Perform parallel processing on chunks
        processed_chunks = pool.map(process_chunk, df_chunks)

        # Concatenate the processed chunks back into a single DataFrame
        processed_df = pd.concat(processed_chunks)

        # Write the stemmed data to the output CSV file
        processed_df.to_csv(output_file_path, index=False, encoding='utf8')
        print(f"Stemmed data has been written to {output_file_path}")
    except FileNotFoundError:
        print(f"File not found: {input_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

