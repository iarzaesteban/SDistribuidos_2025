import { useState } from "react";
import { COORDINADOR_URL } from "../../constants";
import { base64 } from "@scure/base";
import { ed25519 } from "@noble/curves/ed25519";
import { bytesToHex } from "@noble/hashes/utils";

export const useCreateTask = () => {
    const [targetPubKey, setTargetPubKey] = useState<string>("");
    const [userPubKey, setUserPubKey] = useState<string>("");
    const [userPrivKey, setUserPrivKey] = useState<Uint8Array | null>(null);
    const [amount, setAmount] = useState<string>("");
    const [signature, setSignature] = useState<string>("");
    const [timestamp, setTimestamp] = useState<string>("");
    const [generatedKey, setGeneratedKey] = useState<boolean>(false);
    const [isSigned, setIsSigned] = useState<boolean>(false);
    const [response, setResponse] = useState<string>("");

    const description = "Transacción desde frontend";

    const handleGenerateKeys = async () => {
        const privKey = ed25519.utils.randomPrivateKey();
        const pubKeyBytes = await ed25519.getPublicKey(privKey);

        const pubKeyHex = bytesToHex(pubKeyBytes);

        setUserPrivKey(privKey);
        setUserPubKey(pubKeyHex);

        const targetPriv = ed25519.utils.randomPrivateKey();
        const targetPub = await ed25519.getPublicKey(targetPriv);
        const targetPubB64 = base64.encode(targetPub);

        setTargetPubKey(targetPubB64);
        setGeneratedKey(true);
        setIsSigned(false);
        setSignature("");
    };

    const handleSignTask = async () => {
        if (!userPrivKey || !userPubKey || !targetPubKey || !amount) {
            alert("Faltan datos para firmar.");
            return;
        }

        const ts = new Date().toISOString().replace('Z', '+00:00');
        setTimestamp(ts);

        const amountFormatted = parseFloat(amount).toFixed(1);
        const message = `${userPubKey}${targetPubKey}${amountFormatted}${description}${ts}`;
        const messageBytes = new TextEncoder().encode(message);

        const signatureBytes = await ed25519.sign(messageBytes, userPrivKey);
        const signatureB64 = base64.encode(signatureBytes);

        setSignature(signatureB64);
        setIsSigned(true);
    };

    const handleSubmit = async () => {
        if (!userPubKey || !targetPubKey || !signature || !timestamp) {
            alert("Faltan datos para enviar.");
            return;
        }

        const payload = {
            source: userPubKey,
            target: targetPubKey,
            amount: parseFloat(amount),
            description,
            timestamp,
            sign: signature,
        };

        try {
            const res = await fetch(`${COORDINADOR_URL}/new-task`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            const result = await res.json();
            console.log("Resultado es:", result);
            setResponse(result.tx)
        } catch (err) {
            console.error("Error al enviar tarea:", err);
            alert("Error al enviar tarea al coordinador.");
        }
    };

    return {
        handleGenerateKeys,
        handleSignTask,
        handleSubmit,
        setAmount,
        setTargetPubKey,
        isSigned,
        response,
        generatedKey,
        amount,
        targetPubKey,
        userPubKey,
        signature
    }
};
