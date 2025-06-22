import { useState } from "react";
import { COORDINADOR_URL } from "../../constants";
import { base64 } from "@scure/base";
import { ed25519 } from "@noble/curves/ed25519";
import { bytesToHex } from "@noble/hashes/utils";

type KeyPair = {
    priv: Uint8Array;
    pubHex: string;
};

export const useStressTask = () => {
    const [keysAmount, setKeysAmount] = useState<number>(0);
    const [tasksAmount, setTasksAmount] = useState<number>(0);
    const [response, setResponse] = useState<string>("");

    const description = "Transacción desde StressTask Frontend";

    const generateKeyPairs = async (count: number): Promise<KeyPair[]> => {
        const keyPairs: KeyPair[] = [];
        for (let i = 0; i < count; i++) {
            const priv = ed25519.utils.randomPrivateKey();
            const pub = await ed25519.getPublicKey(priv);
            const pubHex = bytesToHex(pub);
            keyPairs.push({ priv, pubHex });
        }
        return keyPairs;
    };

    const handleSubmit = async () => {
        if (keysAmount <= 1 || tasksAmount <= 0) {
            alert("Ingresar cantidades válidas (mínimo 2 claves, 1 tarea).");
            return;
        }

        // 1. Generar pares de claves
        const keyPairs = await generateKeyPairs(keysAmount);

        const tasks = [];
        for (let i = 0; i < tasksAmount; i++) {
            const sourceIdx = Math.floor(Math.random() * keyPairs.length);
            let targetIdx = Math.floor(Math.random() * keyPairs.length);

            while (targetIdx === sourceIdx) {
                targetIdx = Math.floor(Math.random() * keyPairs.length);
            }

            const sourceKeyPair = keyPairs[sourceIdx];
            const targetPubKey = keyPairs[targetIdx].pubHex;
            const amount = (Math.random() * 100).toFixed(1);
            const ts = new Date().toISOString().replace('Z', '+00:00');
            
            const message = `${sourceKeyPair.pubHex}${targetPubKey}${amount}${description}${ts}`;
            const messageBytes = new TextEncoder().encode(message);
            const signatureBytes = await ed25519.sign(messageBytes, sourceKeyPair.priv);
            const signatureB64 = base64.encode(signatureBytes);


            const payload = {
                source: sourceKeyPair.pubHex,
                target: targetPubKey,
                amount: parseFloat(amount),
                description,
                timestamp: ts,
                sign: signatureB64,
            };

            tasks.push(payload);
        }

        try {
            await Promise.all(tasks.map(async (task) => {
                const res = await fetch(`${COORDINADOR_URL}/new-task`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(task),
                });
                return res.json();
            }));

            setResponse(`¡${tasks.length} tareas enviadas exitosamente!`);
        } catch (err) {
            console.error("Error al enviar tareas:", err);
            alert("Error al enviar tareas al coordinador.");
        }
    };

    return {
        keysAmount,
        tasksAmount,
        setKeysAmount,
        setTasksAmount,
        handleSubmit,
        response,
    };
};
