"""Module which defines a graph node feature update based on NNConv."""

from torch import nn

from torch_geometric.nn import NNConv

from mlreco.models.layers.common.mlp import MLP

__all__ = ['NNConvNodeLayer']


class NNConvNodeLayer(nn.Module):
    """NNConv module for extracting graph node features.

    Source: https://arxiv.org/abs/1704.02901
    """
    name = 'nnconv'

    def __init__(self, node_in, edge_in, glob_in, out_channels,
                 mlp, aggr='max', **kwargs):
        """Initialize the MLPs which are used to update the node features.

        Parameters
        ----------
        node_in : int
            Number of input node features
        edge_in : int
            Number of input edge features
        glob_in : int
            Number of input global features for the graph
        out_channels : int
            Number of output node features
        mlp : dict
            Configuration of the node update MLP
        aggr : str, default 'add'
            Node feature aggregation method
        **kwargs : dict
            Extra parameters to be passed to the NNConv layer
        """
        # Initialize the parent class
        super().__init__()

        # Initialize the underlying edge feature MLP
        mlp = MLP(edge_in, **mlp)
        linear = nn.Linear(mlp.feature_size, node_in*out_channels)
        edge_model = nn.Sequential(mlp, linear) 

        # Initialize the layer
        self.feature_size = out_channels
        self.nnconv = NNConv(
                node_in, out_channels, nn=edge_model, aggr=aggr, **kwargs)

    def forward(self, node_feats, edge_index, edge_feats, *args):
        """Pass a batch of node/edges through the edge update layer.

        Parameters
        ----------
        node_feats : torch.Tensor
            (C, N_c) Node features
        edge_index : torch.Tensor
            (2, E) Incidence matrix
        edge_feats : torch.Tensor
            (E, N_e) Edge features
        *args : list, optional
            Other parameters passed but not needed

        Returns
        -------
        torch.Tensor
            (C, N_o) Updated node features
        """
        return self.nnconv(node_feats, edge_index, edge_feats)
