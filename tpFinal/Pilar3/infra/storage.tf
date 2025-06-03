#######################################################
# storage.tf – StorageClass Zonal SSD para GKE (CSI)  #
#######################################################

resource "kubernetes_storage_class" "zonal_ssd" {
  metadata {
    name = "zonal-ssd"
  }

  storage_provisioner = "pd.csi.storage.gke.io"

  parameters = {
    type = "pd-ssd"
    # No ponemos "replication-type", así se crea un disco zonal
  }

  # Podés dejar el binding mode por defecto (Immediate)
  # volume_binding_mode = "Immediate"
}
