param(
    [string]$texto_base = "TEST"
)

# Definición de tests
$tests = @(
    @{ Label = "A"; Prefix="000"; Start=0; End=100000 },
    @{ Label = "B"; Prefix="0000"; Start=0; End=1000000 },
    @{ Label = "C"; Prefix="00000"; Start=0; End=5000000 },
    @{ Label = "D"; Prefix="0000"; Start=1000000; End=2000000 }
)

# Archivo de salida CSV
$outCsv = "results.csv"
"Case,Type,Prefix,Range,Time_s" | Out-File -FilePath $outCsv -Encoding utf8

foreach ($test in $tests) {
    $case = $test.Label
    $prefix = $test.Prefix
    $range = "$($test.Start)-$($test.End)"
    foreach ($type in @("CPU","GPU")) {
        $exe = if ($type -eq "CPU") { ".\brute_range_cpu.exe" } else { ".\brute_range_gpu.exe" }
        Write-Host "Running $type test $case..."
        $output = & $exe $texto_base $prefix $test.Start $test.End
        # Se asume que la última línea contiene "Tiempo total: X.XXX segundos"
        $lastLine = $output[-1]
        if ($lastLine -match "Tiempo total:\s*([\d\.]+)\s*segundos") {
            $time = $matches[1]
        } else {
            $time = "NA"
        }
        "$case,$type,$prefix,$range,$time" | Out-File -FilePath $outCsv -Append -Encoding utf8
    }
}

Write-Host "Tests completed. Results saved in $outCsv"
