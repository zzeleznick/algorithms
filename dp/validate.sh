# Validates program
python main.py example_input.txt test_words.txt test_num.txt > /dev/null
cmp --silent test_words.txt solution_words.txt || echo "interpretation of words incorrect, compare test_words.txt and solution_words.txt"
cmp --silent test_num.txt solution_num.txt || echo "number of interpretations incorrect, compare test_num.txt and solution_num.txt"
