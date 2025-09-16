package lessons

import (
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

func IsPalindrome(text string) bool {
	filtered := filteringRE.ReplaceAllString(text, "")
	filtered = strings.ToLower(filtered)
	runes := []rune(filtered)
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
