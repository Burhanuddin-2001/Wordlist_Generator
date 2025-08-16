from itertools import product
from math import ceil,floor
from tqdm import tqdm

from argparse import ArgumentParser

def determine_max_repetition(wall,length):
    total_size=0
    repetition=1
    while True:
        current_combination=length**repetition
        total_size+=current_combination
        if total_size>wall:
            return repetition-1
        repetition+=1

def generate_wordlist(words,target=None,display=False):
    l=len(words)

    if target:
        shortest_word = min(words, key=len)
        longest_word = max(words, key=len)

        min_word_len = len(shortest_word)
        max_word_len = len(longest_word)
        maximum_repetition=ceil(target/min_word_len)
        minimum_repetation=floor(target/max_word_len)
    else:
        minimum_repetation=1
        feasible_limit=38146972655
        maximum_repetition=determine_max_repetition(feasible_limit,l)
        
    with open("wordlist.txt","w") as file:
        for i in range(minimum_repetation, maximum_repetition):
            combinations=product(words,repeat=i)
            total_for_this_iteration= l**i
            for item in tqdm(combinations,total=total_for_this_iteration, desc=f"Loop {i}"):
                temp="".join(item)
                if target is not None and len(temp)!=target:
                    continue
                temp+="\n"
                
                if display:
                    print(temp,end="")
                else:
                    file.write(temp)




    
def main():

    parser=ArgumentParser(description="Wordlist Generator Program")

    parser.add_argument("--filepath",dest="filepath",required=True,help="Enter the path of your file that contains the words for generation inbetween double quotes.")

    parser.add_argument("--display",dest="display",action="store_true",help="Use this tag if you need to pass the generated string directly into programs like hashcat and others. \nThis will not store the generations into your disk.")

    parser.add_argument("--length",dest="passwordlength",type=int,help="Specify the length of your password for exact generations.")

    arguments=parser.parse_args()
    #reading file to know the possible words
    try:
        with open(arguments.filepath,"r") as file:
            words=file.readlines()
    except FileNotFoundError:
        print("Please create a file name 'file.txt' and add the words to it which you want your wordlist to be based on. Each word should be present in a unique line of its own.")
    
    words=[w.strip() for w in words]
    print(words)
    
    generate_wordlist(words,arguments.passwordlength,arguments.display)




    
if __name__=="__main__":
    main()



