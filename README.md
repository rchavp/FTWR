# Follow The White Rabbit
This is a solution (in Python) to Trustpilot's interviewing problem specified [here](https://followthewhiterabbit.trustpilot.com/cs/step3.html)

***
### TL;DR
With Docker installed, just open a terminal window and run the following from the repository's root folder. This will install the image (based on Alpine so minimal footprint): 
``
docker build -t ftwr .
``

Then execute a container from this image with this command: 
``
docker run --name ftwr-ins -it --rm ftwr
``

The test will be automatically executed, showing the matching anagrams as they appear.

All 3 anagrams matching the 3 hashes are resolved in around 10 seconds on my machine (Rizen 5, QuadCore, 8GB RAM, no GPU involved)
***
## Problem analysis

Searching for anagrams is usually a permutation problem. In this particular case the target anagram is hashed so any correlation that could eventually help in the search is lost given that md5 is a one way uncorrelated function. 
This means that our search will have to at least find suitable anagram candidates in order to test which one matches the target. 
Finding anagrams is typically a O(!) problem when doing it very naively or O(n^2) when using a recursive approach. This makes the problem very hard to compute by sheer brute force for even moderately large numbers of n. 
The quest here then is to determine sufficiently good ways of transforming as much of the O(n^2) problem into lower search spaces like O(n) or even O(1) if at all possible. Given that we already know that O(n^2) is better that O(!) and that recursion is a good way to implement the former, we will try to figure out a recursive solution as a starting point. 
We will tackle the problem in an incremental way.
### Approach 1: Naive search
An anagram of a word is composed by the concatenation of n known and valid words whose length after concatenation is the same as the input anagram's. If we have an anagram **A** and a list of words **Lw** with **n** words, perhaps we can calculate all the permutations of A where the result set is of length **s**. After that then we may hash every permutation and check it against the target (or better yet check the target while calculating the permutations). If this were to work we may transform the problem into a O(n^2) perhaps?
Our input anagram is 18 characters long, so in order to get an idea of how many options we will need to check, we can just calculate the number of permutations of A of size len(A) which is an [analytical problem](https://www.calculatorsoup.com/calculators/discretemathematics/permutations.php). The result is a staggering 6.402373705E+15 permutations! This is impractical for any computers that I know of and may take an unreasonable long time to finish.
### Approach 2: Better naive search
We can do better by focusing the search on the word list **Lw**. For example, we can iterate through **Lw** with **n** elements and for each word **w** see if it fits into the anagram **A**. If it does, then we recursively call this search with a subset of **A** minus the current word **w**. The recursion can stop by either the word **w** not fitting into **A** or when there is no more subsets of **A** after removing **w** in the current recursion (which means we found an anagram).
We can see this approach is recursive as it divides a problem with an anagram **A** and a word list **Lw** of size **n** into subsets of problems with anagrams **A-w** and wordlists of size **n-1** 
This is indeed a O(2^n) problem.
### Reducing the search space
Following the recursive O(2^n) approach we can try to optimize it in several ways:
1. Reduce the number of **n** for each list of words **Lw** in each recursive iteration.
2. Reduce the maximum depth of each iteration. This is a very important optimization step. The recursive search we need to do is in fact a tree search, where the depth of the leaf nodes is determined by the stop condition of the recursion, which means we can go as deep as the number of valid words that can fit into the anagram **A**. This is problematic because every recursion call can potentially have a big word list **L** which will in turn can generate **n** branches of recursion, and so on (a potential explosion of permutations). By the laws of exponential growth this can get bad very quickly so we should strive for methods that can minimize the tree depth.
3. Some search branch's traversals could be equivalent. For example, we can start with the word "dog" then "cat" and then "rat", yet another branch of recursion can start with "cat" then "rat" and then "dog". If we think about this, the permutations of these 3 words may be shorter that the entire permutations performed by a each branch. In other words, we may calculate the branch "dog"->"cat"->"rat", and assuimg the 3 words make a valid anagram, we can test the md5s of the permutations of the 3 words at once, and then when the top recursion loop gets to "cat" or "rat", it will ignore those branches and skip the recursion for those, as those were already tested. This is of course, a dynamic programming technique which reduces an O(2^n) search towards a O(1) search by memoization. 
Let's discuss these techniques further:

#### Reducing n for each word list
This can be done readily by making sure each word **w** in the list can fit into the anagram **A**. For this we just filter out the word list **Lw** to remove words that cannot be part of **A**
#### Reducing recursion maximum depth
The recursion max depth can be reduced by trying to reach the recursion's exit condition as fast as possible. For this purpose we can try to bias the algorithm towards finding anagrams with fewer words (each word implies a new recursion branch). One may think that starting with the larger words will achieve this, however this is not entirely correct on average. The problem is that even if we start with a long word for a branch search, we will anyway end up with a list of words for the next recursion that will contain small words. Hence the search can still explode by creating too many levels of recursive branching. 
A more balance approach is to bias the search algorithm to start with words that are around half of the length of the anagram. In this case, on average, it is very likely that subsequent recursion levels have words with a size no that much lower that the parent recursion's branch.
#### Taking into account redundancy
Finally, we can capitalize on another feature of this problem which we haven't explored before. Anagrams can also be described as multisets or hyper-vectors, which means that the reason we may have similar branches in the search tree is because the solutions we are checking for are in fact the same multiset. 
For example, "dog", "cat" and "rat" create a multiset of (d,o,g,c,a,t,r,a,t) which by definition is an unordered set. The order of the characters **only** matters when md5 checking for the actual anagrams (which are ordered sets). This key point means we can transform our word list into a list of the multisets (or hyper-vectors) of each word, and use this list as the basis of recursion. Then, we can memoize the searches we do based on the multiset value of the current word (as a key to a hashmap for ex.) so that we can skip entire branches of search. Now this means that for every anagram candidate we found, which will be the same multiset as the original anagram itself, we will still need to check for the md5 of all the permutations of the original words that formed the multisets we used to create the anagram candidate. 
In other words, per the example above, if we find that the multiset (d,o,g,c,a,t,r,a,t) is a valid anagram candidate, we will then need to know that the actual words "dog", "cat" and "rat" were used and then check all the permutations of these for their md5s. The only way this new level of iteration would not render the benefits of multisets useless is that the search space of the latter can be biased to be smaller that the former. In other words, if the number of words in an anagram candidate is small, the permutation number for these words in the candidate will likely be smaller that performing a full branch recursive search. 
This means that we may use this approach of using multisets if we combine it with the previous approach of reducing the recursion maximum depth. Otherwise it may be counterproductive, but fortunately in this case we can try it out with a good chance of ripping its benefits.

### Conclusion

Taking all the previous factors into consideration, the algorithm I chose was the following:

1. Read the list of English words and make sure we clean it up, especially of short words that are not actually English words (this reduces the recursion depth massively in the case of one letter words like "k" or "p" which are not actually English words to start with). We can also filter out characters outside the English alphabet (26 letters) as we assume the target secret anagrams will be composed of English words. We call this list **Lw**
2. With an optimal list of words we create a new list of the multisets of those words **Lmsw**.
3. Some words in **Lw** may correspond to the same multiset in **Lmsw**. For example, "god" and "dog" correspond to the same multiset (d,g,o). Since **Lmsw** will only have multisets, we need to store the relationship between the multiset and their respective words. For this reason we create a hashmap where the key is the multiset** and the value is a list of the respective words. We call this map **Mms->w**
4. Now we can start the recursion. For each call to the recursion, we will pass the anagram we are testing (as a multiset) and a list of words as multisets (**Lmsw** instead of **Lw**) that we will **first** filter to discard the ones that can't fit into the anagram. On each recusrion level, the recursion will exit if no words can fit into the anagram (so we could not find a valid anagram candidate for this recursion) or if the anagram we got is empty (so no more sub anagrams to check which means we have a valid candidate). Whenever we find an anagram candidate we calculate the md5s of its permutations by using the map **Mms->w**. If the recursion didn't end, we take the word list (**Lmsw**) that was passed to the function, and we iterate for each element (which is a multiset instead of a word) and **first** we check if we have done this search before. We do this by using a map we will call **Mdone**. If **Mdone** contains the current iteration's word (multiset) then we skip it, otherwise we add the word to **Mdone** (to signal that this search branch is covered) and then start a new recursion level call by passing the subset of the anagram **A-w** (the anagram minus the current word in the iteration) and a subset of the word list without elements that cannot be part of **A-w**. And so on.

### Special notes
It is important to keep in mind that this whole approach is not meant to provide a guaranteed short result within the search space. Given the nature of the problem, as we saw at the beginning of this discussion, the best we can do is to provide an algorithm that will bias a O(2^n) towards a O(n^2) or even O(n). But the actual time it will take is never determined nor certain. Only the reduction of the search space is certain.

### Results
Implementing this code in Python (to take advantage of some very well optimized libraries for Combinatorial calculations as well as for efficient array splicing and manipulation) we got a result like this:

```
Start Time: 1603712780.3887076
----------------------------------
Raw words: 99175
Good words: 72740
Applicable words: 1766
Applicable words as hypervectors(multisets): 1168
Anagram length: 18

!!!! Found second secret at 2.481304883956909 seconds: "ty outlaws printouts"
!!!! Found third secret at 2.815124988555908 seconds: "wu lisp not statutory"
!!!! Found first secret at 9.608782529830933 seconds: "printout stout yawls"
-------------------------------------------------------

All secrets found. Total time: 9.608872175216675
-------------------------------------------------------
```

Which is an average time of around 10s on my laptop.
An interesting detail is that this algorithm found the first secret last, which may be an indicator that there may be an even better optimization technique that I didn't explore. 
Nevertheless I hope this is good enough for the purposes of this exercise. 
Another aspect I didn't explore was to implement this in pure C or C++ to leverage a more efficient use of memory and most of all immutable array manipulation which could significantly reduce the splicing and sub-setting of the word lists in memory.
