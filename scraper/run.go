package main
import ("fmt"
		"bytes"
		"os/exec"
		"time")

//why use golang for the systemd ExecStart? because threading might be easier?
var CMD = []string{"-c", "source ../venv/bin/activate; python scraper.py"}
var WAIT = time.Second*3

func main() {
	for {
		var cmd *exec.Cmd = exec.Command("bash", CMD...)
		var out bytes.Buffer
		cmd.Stdout = &out
		err := cmd.Run()
		if err != nil {
			fmt.Println(err)
		} else {
			fmt.Println(out.String())
		}
		time.Sleep(WAIT)
	}
}