package lessons

import (
	"fmt"
	"os"
	"path/filepath"
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

func IsPalindrome(text string, useFilter bool) bool {
	if useFilter {
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

func printEvenIndexRec(numList []int, i int) {
	if i >= len(numList) {
		return
	}
	fmt.Println(numList[i])
	printEvenIndexRec(numList, i+2)
}

func printEvenIndex(numList []int) {
	printEvenIndexRec(numList, 0)
}

func secondMax(nums []int) (int, bool) {
	if len(nums) < 2 {
		return 0, false
	}
	a, b := nums[0], nums[1]
	var max1, max2 int
	if a >= b {
		max1, max2 = a, b
	} else {
		max1, max2 = b, a
	}
	return secondMaxRec(nums, 2, max1, max2), true
}

func secondMaxRec(nums []int, i, max1, max2 int) int {
	if i == len(nums) {
		return max2
	}
	x := nums[i]
	if x > max1 {
		max2, max1 = max1, x
	} else if x > max2 {
		max2 = x
	}
	return secondMaxRec(nums, i+1, max1, max2)
}

func FindAllFiles(dir string) ([]string, error) {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return nil, err
	}

	out := make([]string, 0, len(entries))
	for _, e := range entries {
		path := filepath.Join(dir, e.Name())
		if e.IsDir() {
			sub, err := FindAllFiles(path)
			if err != nil {
				return nil, err
			}
			out = append(out, sub...)
		} else {
			out = append(out, path)
		}
	}
	return out, nil
}
