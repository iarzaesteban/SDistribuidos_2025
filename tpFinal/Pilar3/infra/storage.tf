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
  }

  volume_binding_mode = "WaitForFirstConsumer"
}

