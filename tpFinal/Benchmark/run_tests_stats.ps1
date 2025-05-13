param(
    [string]$texto_base = "TEST",
    [int]$reps = 5
)

# Definición de tests (A–D + test de no solución)
$tests = @(
    @{ Label = "A"; Prefix="000"; Start=0; End=100000 },
    @{ Label = "B"; Prefix="0000"; Start=0; End=1000000 },
    @{ Label = "C"; Prefix="00000"; Start=0; End=5000000 },
    @{ Label = "D"; Prefix="0000"; Start=1000000; End=2000000 },
    @{ Label = "X"; Prefix="ffffff"; Start=0; End=100000 }  # test de no solución
)

$outCsv = "results_detailed.csv"
"Case,Type,Prefix,Range,Iteration,Time_s" | Out-File -FilePath $outCsv -Encoding utf8

for ($i = 1; $i -le $reps; $i++) {
    foreach ($test in $tests) {
        $case = $test.Label
        $prefix = $test.Prefix
        $range = "$($test.Start)-$($test.End)"
        foreach ($type in @("CPU","GPU")) {
            $exe = if ($type -eq "CPU") { ".\brute_range_cpu.exe" } else { ".\brute_range_gpu.exe" }
            Write-Host "Running $type test $case (iter $i)..."
            $output = & $exe $texto_base $prefix $test.Start $test.End
            $lastLine = $output[-1]
            if ($lastLine -match "Tiempo total:\s*([\d\.]+)\s*segundos") {
                $time = $matches[1]
            } else {
                $time = "NA"
            }
            "$case,$type,$prefix,$range,$i,$time" | Out-File -FilePath $outCsv -Append -Encoding utf8
        }
    }
}

Write-Host "Repeticiones completadas. Detalle en results_detailed.csv"
