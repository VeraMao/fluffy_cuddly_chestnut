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

# find two consecutive decimal characters
re.findall('[0-9][0-9]', d) 结果是['12', '12']
123 中的 23 不符合“连续两个数字”的独立匹配，因为它属于三个数字的一部分。

# alphabetic characters
re.findall('[a-zA-Z][a-z][a-z][a-z]', d)
结果是['ciao', 'Good']

但是这里没有找到12hi里的hi, 如果想要找hi的话要用re.findall(r'[a-zA-Z]+', d)

. 是一个特殊字符, 在有mix of characters或者没有特定的pattern的时候很有用
例如: 用四个点来匹配四个字母
re.findall(r"....$", d) # $表示结尾, 这里是找了
结果是['12hi']

'''

