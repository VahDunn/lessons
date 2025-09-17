package lessons

import (
	"fmt"
	"regexp"
	"strings"
)

func toPower(n int, m int) int {
	if m == 0 {
		return 1
	}
	if m < 0 {
		return 1 / toPower(n, -m)
	}
	return n * toPower(n, m-1)
}

func digitSum(n int) int {
	if n < 0 {
		n = -n
	}
	if n < 10 {
		return n
	}
	return n%10 + digitSum(n/10)
}

func listLength(ll []int) int {
	if len(ll) == 0 {
		return 0
	}
	return listLength(ll[1:]) + 1
}

var filteringRE = regexp.MustCompile(`[^\p{L}\p{N}]+`)

func IsPalindrome(text string, needFilter bool) bool {
	if needFilter {
		text = filteringRE.ReplaceAllString(text, "")
		text = strings.ToLower(text)
	}
	runes := []rune(text)
	return checkPalindrome(runes, 0, len(runes)-1)
}

func checkPalindrome(runes []rune, left, right int) bool {
	if left >= right {
		return true
	}
	if runes[left] != runes[right] {
		return false
	}
	return checkPalindrome(runes, left+1, right-1)
}

func printEvenRec(numList []int, i int) {
	if i >= len(numList) {
		return
	}
	if numList[i]%2 == 0 {
		fmt.Println(numList[i])
	}
	printEvenRec(numList, i+1)
}

func printEven(numList []int) {
	printEvenRec(numList, 0)
}
