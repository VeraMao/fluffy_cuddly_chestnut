'''
Regular Expressions (RegEx) Notes
- sequence of characters that define a search pattern
- search(), match(), findall(), split(), sub()

总结:
match: 只在字符串的开头匹配
fullmatch: 匹配整个字符串
search: 在字符串中搜索匹配
findall: 返回所有匹配的字符串
split: 根据pattern分割字符串
sub: 替换字符串中的pattern

r的作用是把字符串转换成raw string, 也就是不会把\当成转义字符

------------------------------------------------

1. Simple Search, takes 2 arguments: pattern and string, if not successful, returns None
word = input("Enter a word: ")
pattern = 'as'

if re.search(pattern, word): 
    print("The pattern matches the word")
else:
    print("The pattern doesn't match the word")

注意:
print(re.search(r"regex", a)) 结果是 <re.Match object; span=(28, 33), match='regex'> span指的是匹配的位置, match指的是匹配的内容
type(re.search(r"regex", a)) 结果是 re.Match
可以用作boolean: bool(re.search("regex", a))
-----

Example: 
# create an empty list named 'pats' for patterns
pats = []

# any string where an 'a' occurs, followed by exactly two other characters, and an 's' occurs
pats.append('a..s')

# any string where an 'a' occurs, followed by any number of characters, and an 's' occurs
pats.append('a.*s')

print(pats) 结果是['a..s', 'a.*s']

word = input('Enter a word: ')

for pat in pats:
    if re.search(pat, word):
        print("The pattern", pat, "matches")
    else:
        print("The pattern", pat, "doesn't match")
        
# letter 'a' does not have to be at the beginning for example paoos matches in both

------------------------------------------------

2. findall(), return a list of all matches
a = "Let's find the word 'regex' using regexes!"
re.findall(r'regex', a) 结果是['regex', 'regex']

Raw strings in Python are normal strings but prefixed with an "r": useful as they allow to interpret the backslash \ as a literal character, rather than an escape character. 

* `re.findall("\n", text)`: matches a new line in text
* `re.findall(r"\n", text)`: matches a literal backlash followed by the character 'n' in text

------------------------------------------------

3. match(), 和search很像, 但是只在字符串的开头匹配

b = "123abc"

if re.match("abc", b):
    print("abc found with re.match")
    
if re.search("abc", b):
    print("abc found with re.search")

结果是 abc found with re.search

注意: re.match('pattern') = re.search('^pattern'). ^的意思是start of the string

------------------------------------------------

4. split(), 把text根据pattern分割成list
sub(), 替换text中的pattern

c = "This is a sentence! re.split will split it based on the pattern! re.sub will replace the pattern"
re.split(r"!", c) #这里的pattern是感叹号, 也就是根据感叹号分割这个句子
结果是
['This is a sentence',
 ' re.split will split it based on the pattern',
 ' re.sub will replace the pattern']

re.sub(r"!", ";", c) #把感叹号替换成分号
结果是 'This is a sentence; re.split will split it based on the pattern; re.sub will replace the pattern'

------------------------------------------------
Special Characters:
[abc]: 在方括号中的任何字符将会被匹配
[^abc]: 除了abc之外的任何字符将会被匹配
[0-9]: 0到9之间的任何数字将会被匹配
^: 匹配字符串的开头
$: 匹配字符串的结尾
.: 匹配任何字符
\: 转义字符, 用来匹配特殊字符, 例如\.匹配句号
\d: 匹配1个digit的数字, 等价于[0-9]
\D: 匹配1个non-digit的字符, 等价于[^0-9]
\w: 匹配1个word字符, 等价于[a-zA-Z0-9_]
\W: 匹配1个non-word字符, 等价于[^a-zA-Z0-9_]
\s: 匹配1个whitespace字符, 等价于[\t\n\r\f\v]
\S: 匹配1个non-whitespace字符, 等价于[^\t\n\r\f\v]
\b: 匹配一个单词的边界, 比如\bword\b匹配"word"但是不匹配"words" - whole words only search

在一个方括号内的就是一个character class, 如果想看一个string有没有具体的字符, 可以用这个方法

Example:
d = 'ciao_Good_123_12hi'

# find three consecutive decimal characters
re.findall('[0-9][0-9][0-9]', d) 结果是['123'] 
更简洁的方法有:
re.findall(r'\d{3}', d) or re.findall(r'[0-9]{3}', d)

# find two consecutive decimal characters
re.findall('[0-9][0-9]', d) 结果是['12', '12']
123 中的 23 不符合“连续两个数字”的独立匹配，因为它属于三个数字的一部分。
更简洁的方法有:
re.findall(r'\d{2}', d) or re.findall(r'[0-9]{2}', d)

# alphabetic characters
re.findall('[a-zA-Z][a-z][a-z][a-z]', d)
结果是['ciao', 'Good']

但是这里没有找到12hi里的hi, 如果想要找hi的话要用re.findall(r'[a-zA-Z]+', d)

如果在找[]外面的字符, ^表示开头; 如果找在[]没有的字符, ^表示not
re.findall(r"^[a-z]", d) #找开头是小写字母的字符

. 是一个特殊字符, 在有mix of characters或者没有特定的pattern的时候很有用
例如: 用四个点来匹配四个字母
re.findall(r"....$", d) # $表示结尾, 这里是找了   结果是['12hi']

用\和re.split()的情况:
e = "This is a sentence. This is a seoncd sentence."
re.split(r"\.\s+", e) 
解释: \.的意思是句号, \s+的意思是一个或多个空格, 所以这里是根据句号和一个或多个空格来分割这个句子

or 用 |
f = "My favorite color is red and Anne's favorite colour is green"
re.findall(r"color|colour", f)
结果是['color', 'colour']

g = "This&is#MACS&30122%at#UChicago." 
re.sub(r"&|#|%|#", " ", g) 
结果是 'This is MACS 30122 at UChicago.'

re.sub(r"[&#%#]", " ", g)
结果是 'This is MACS 30122 at UChicago.'

Common Value as Sets - A-Z, a-z, 0-9
i = "There are four PAs: PA1, PA2, PA3, PA4. They make 50% of the final grade"
re.findall(r"PA\d, i) 结果是['PA1', 'PA2', 'PA3', 'PA4']
re.findall(r"PA\D, i) 结果是['PAs'] #\D是non-digit
re.findall(r"PA\w, i) 结果是['PA1', 'PA2', 'PA3', 'PA4', 'PAs'] #\w是word character
re.findall(r"\W, i) 结果是[' ', ' ', ' ', ' ', ' ', '%', ' '] #\W是non-word character
re.findall(r"final\sgrade", i) 结果是['final grade'] #\s是whitespace character

------------------------------------------------
Quantifiers:
*: match 0 or more 单个字符, 意思是
+: 1 or more 单个字符
?: 0 or 1 单个字符
{m}: exactly m occurrences
{m, n}: m to n occurrences
{m, }: m or more occurrences
{, n}: 0 to n occurrences

re.findall(r"\d{2,3}-\d{4,}", l) # {n, m} at least n times, at most m times
这里的意思是找两到三个数字, 然后一个短横线, 然后四个或者更多的数字

------------------------------------------------
Greedy & Non-Greedy Matching:
Lazy or Non-Greedy Matching: *?, +?, ??, {m,n}?, {,}?
- Match as little text as possible

n = "abc abbbc abbcabbbc"
Greedy Matching: match "a", 然后followed by 1或者更多个word characters, 在c结束
- re.findall(r"a\w+c", n) 结果是['abc', 'abbbc', 'abbc']
Note that "abbcabbc" would never be matched, as it would lazily stop at 'c'. Instead, there are two matches: "abbc" and "abbbbc". 

o = "AAAGCGCCCGGGA" 
Greedy Matching: re.findall(r"G.*G, o) 这里是在G和G之间找任何字符, 结果是['GCGCCCGG']
Lazy Matching: re.findall(r"G.*?G, o) 结果是['GG', 'GGG']  区别是在*后面加了一个?号, 也就是说尽可能少的匹配

------------------------------------------------
Grouping:
match = re.search("(pattern1)(Pattern2)", string)
if match:
    print(match.group(1)) - prints the string that matches pattern 1
    print(match.group(2)) - prints the string that matches pattern 2
    print(match.group()) - prints the entire string that matches the pattern

match = re.search('(\w+)(\s)(\d.+)', "Apple 3.99")
print(match.group(1))  # group 1 is (\w+)
print(match.group(3))  # group 3 is (\d.+)
解释: (\w+)是word character, (\s)是whitespace, (\d.+)是digit, 所以找到的是Apple和3.99

s = "Hello world!"
s1 = "This works only without commas or apostrophes."
s2 = "Test if s1 is true, with this sentence that contains a comma."

group = r'\w+(\s\w+)*[.?!]'
       
print(re.fullmatch(group, s)) 结果是: None, 因为没有句号
print(re.search(group, s1)) 结果是: <re.Match object; span=(0, 36), match='This works only without commas or apostrophes.'>
print(re.search(group, s2)) 结果是: <re.Match object; span=(0, 64), match='Test if s1 is true, with this sentence that contains a comma.'>

Lookahead and Lookbehind:
Positive lookahead: e1(?=e2) - Matches e1 only if it is followed by e2
Negative lookahead: e1(?!e2) - Matches e1 only if it is not followed by e2
Positive lookbehind: (?<=e2)e1 - Matches e1 only if it is preceded by e2
Negative lookbehind: (?<!e2)e1 - Matches e1 only if it is not preceded by e2

r = 'footprint footstool'
re.findall(r'foot(?=print)', r)
foot(?=print)的意思是找foot后面是print的foot, 结果是['foot']

re.findall(r'foot(?!print)', r)
foot(?!print)的意思是找foot后面不是print的foot, 结果是['foot']

Backreferences:
- A backreference is a reference to a capturing group that has already been matched

q = 'ciao ciao hope you are doing well'
re.findall(r'\b(\w+)\b\s+\1\b', q)
结果是['ciao'], 这里的\b是word boundary, \w+是word character, \s+是whitespace, \1是backreference, 也就是说找到了两个相同的单词

u = '1234 2323 84208420 9339 11 602601'
re.findall(r'\b(\d+)\1+\s+\b', u)
这里的\d+是digit, \1是backreference, \s+是whitespace, 结果是['2323', '84208420', '11']



'''

