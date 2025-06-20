import axios from "axios";
import { COORDINADOR_URL } from "../../constants";
import { useEffect, useState } from "react";
import type { TransactionResponse, TransactionStatus, RegisteredWorkersResponse } from "../../types/types";

export const useBlockchainViewer = () => {
    const [error, setError] = useState<string>("");
    const [transaction, setTransaction] = useState<TransactionStatus | null>(null);
    const [status, setStatus] = useState<string>("");
    const [workers, setWorkers] = useState<RegisteredWorkersResponse["workers"]>([]);


    useEffect(() => {
        const fetchWorkers = async () => {
            try {
                const response = await axios.get<RegisteredWorkersResponse>(
                    `${COORDINADOR_URL}/registered-workers`
                );
                setWorkers(response.data.workers);
                setError("");
            } catch (err) {
                setError("Error al obtener los workers");
                console.error(err);
            }
        };

        fetchWorkers();
    }, []);

    const handleSearchTransaction = async (tx_id: string) => {
        try {
            const response = await axios.get<TransactionResponse>(
                `${COORDINADOR_URL}/get-transaction/${tx_id}`
            );

            setTransaction(response.data.tx);
            setStatus(response.data.status);
            setError("");
        } catch (err) {
            setError("Error al obtener la transacción");
            console.error(err);
        }
    };

    return {
        handleSearchTransaction,
        transaction,
        status,
        workers,
        error
    }
}