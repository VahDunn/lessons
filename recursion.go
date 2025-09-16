package lessons

import (
	"strings"
	"unicode"
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

func isPalindromeRec(s string) bool {
	var filtered []rune
	for _, r := range strings.ToLower(s) {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			filtered = append(filtered, r)
		}
	}
	return check(filtered)
}

func check(rs []rune) bool {
	if len(rs) <= 1 {
		return true
	}
	if rs[0] != rs[len(rs)-1] {
		return false
	}
	return check(rs[1 : len(rs)-1])
}
