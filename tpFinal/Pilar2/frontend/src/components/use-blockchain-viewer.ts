import { useState } from "react";
import { COORDINADOR_URL } from "../constants";
import axios from "axios";
import type { Block, GenesisBlockType } from "../types/types";

export const useBlockchainViewer = () => {
    const [blockchain, setBlockchain] = useState<Block[]>([]);
    const [genesisBlock, setGenesisBlock] = useState<GenesisBlockType>();
    const [createTask, setCreateTask] = useState<boolean>(false);
    const [error, setError] = useState<string>("");
    
    const cleanData = () =>{
        setBlockchain([]);
        setGenesisBlock(undefined);
    }
    const handleCreateTask = () => {
        cleanData();
        setCreateTask(!createTask);
    }

    const fetchBlockchain = async () => {
        try {
            cleanData();
            const response = await axios.get(COORDINADOR_URL + '/blockchain');
            setBlockchain(response.data.Blockchain);
            setError("");
        } catch (err) {
            setError("Error al obtener la blockchain");
            console.log(err);
        }
    };

    const fetchGenesisBlock = async () => {
        try {
            cleanData();
            const response = await axios.get(COORDINADOR_URL + '/genesis-block');
            console.log("La respomse es", response)
            setGenesisBlock(response.data);
            setError("");
        } catch (err) {
            setError("Error al obtener el bloque GENESIS");
            console.log(err);
        }
    };
    return {
        fetchBlockchain,
        fetchGenesisBlock,
        handleCreateTask,
        blockchain,
        genesisBlock,
        createTask,
        error
    }
};
