import axios from "axios";
import { COORDINADOR_URL } from "../../constants";
import { useEffect, useState } from "react";
import type { TransactionResponse, TransactionStatus, RegisteredWorkersResponse, InProgressTxResponse, EarringQueueResponse } from "../../types/types";

export const useBlockchainViewer = () => {
    const [error, setError] = useState<string>("");
    const [transaction, setTransaction] = useState<TransactionStatus | null>(null);
    const [status, setStatus] = useState<string>("");
    const [workers, setWorkers] = useState<RegisteredWorkersResponse["workers"]>([]);
    const [inProgressTxs, setInProgressTxs] = useState<TransactionStatus[]>([]);
    const [earringTxs, setEarringTxs] = useState<TransactionStatus[]>([]);

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

    useEffect(() => {
        const fetchInProgressTxs = async () => {
            try {
                const response = await axios.get<InProgressTxResponse>(
                    `${COORDINADOR_URL}/get-in-progress-txs`
                );
                setInProgressTxs(response.data.transactions);
                setError("");
            } catch (err) {
                setError("Error al obtener tareas en progreso");
                console.error(err);
            }
        };

        fetchInProgressTxs();

        const interval = setInterval(fetchInProgressTxs, 10000);

        return () => clearInterval(interval);
    }, []);


    useEffect(() => {
        const fetchEarringQueueTxs = async () => {
            try {
                const response = await axios.get<EarringQueueResponse>(
                    `${COORDINADOR_URL}/get-earrings-transactions`
                );
                setEarringTxs(response.data.transactions);
                setError("");
            } catch (err) {
                setError("Error al obtener tareas pendientes de RabbitMQ");
                console.error(err);
            }
        };

        fetchEarringQueueTxs();

        const interval = setInterval(fetchEarringQueueTxs, 10000);

        return () => clearInterval(interval);
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
        inProgressTxs,
        earringTxs,
        workers,
        error
    }
}