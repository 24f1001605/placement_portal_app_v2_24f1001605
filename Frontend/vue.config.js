const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  chainWebpack: config => {
    // Exclude index.html from CopyPlugin — HtmlWebpackPlugin already handles it
    config.plugin('copy').tap(args => {
      const patterns = args[0].patterns || args[0]
      const publicPattern = Array.isArray(patterns) ? patterns[0] : patterns
      if (publicPattern) {
        publicPattern.globOptions = publicPattern.globOptions || {}
        publicPattern.globOptions.ignore = (publicPattern.globOptions.ignore || []).concat(['**/index.html'])
      }
      return args
    })
  },
  devServer: {
    port: 8080,
    client: { overlay: false },
    proxy: {
      '/api': { target: 'http://localhost:5001', changeOrigin: true }
    }
  }
})
