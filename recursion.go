package lessons

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
