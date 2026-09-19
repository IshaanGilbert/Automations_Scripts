import transformers.utils.import_utils as iu

# Disable Lazy Loader Completely
iu.LazyModule = lambda *args, **kwargs: None
